import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest
from app import App

class AccountsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.db = Path(cls.temp.name) / 'accounts.sqlite3'
        cls.server = App(('127.0.0.1', 0), cls.db)
        cls.port = cls.server.server_port
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.temp.cleanup()

    def request(self, path, data=None, cookie=None, csrf=None, origin=True):
        conn = http.client.HTTPConnection('127.0.0.1', self.port)
        headers = {}
        if data is not None:
            headers['Content-Type'] = 'application/json'
            if origin: headers['Origin'] = f'http://127.0.0.1:{self.port}'
        if cookie: headers['Cookie'] = cookie
        if csrf: headers['X-CSRF-Token'] = csrf
        conn.request('POST' if data is not None else 'GET', path, json.dumps(data) if data is not None else None, headers)
        response = conn.getresponse()
        raw = response.read()
        result = json.loads(raw) if response.getheader('Content-Type', '').startswith('application/json') else raw
        code, cookie = response.status, response.getheader('Set-Cookie')
        conn.close()
        return code, result, cookie

    def test_account_lifecycle_privacy_and_persistence(self):
        credentials = {'username': 'Test_Player', 'password': 'correct horse battery staple'}
        code, result, cookie = self.request('/api/signup', credentials)
        self.assertEqual(code, 201)
        self.assertEqual(result['user']['username'], 'test_player')
        self.assertIn('HttpOnly', cookie)
        self.assertIn('SameSite=Lax', cookie)
        csrf = result['csrf']
        profile = {'display_name': '<script>hello</script>', 'bio': 'Head nod music', 'chess': 'Endgames', 'music': 'Lo-fi', 'avatar': '🎼', 'accent': '#c060ff', 'lichess': 'manny', 'chesscom': ''}
        self.assertEqual(self.request('/api/profile', profile, cookie)[0], 403)
        self.assertEqual(self.request('/api/profile', profile)[0], 401)
        self.assertEqual(self.request('/api/profile', {**profile, 'accent': 'url(evil)'}, cookie, csrf)[0], 400)
        self.assertEqual(self.request('/api/profile', profile, cookie, csrf, origin=False)[0], 403)
        self.assertEqual(self.request('/api/profile', profile, cookie, csrf)[0], 200)
        code, public, _ = self.request('/api/profiles/test_player')
        self.assertEqual(public['profile']['bio'], 'Head nod music')
        self.assertNotIn('password_hash', public['profile'])
        self.assertNotIn('salt', public['profile'])
        self.assertNotIn('csrf', public['profile'])
        with self.server.connect() as conn:
            row = conn.execute('SELECT * FROM users WHERE username=?', ('test_player',)).fetchone()
            self.assertNotEqual(row['password_hash'], credentials['password'])
        self.assertEqual(self.request('/api/signup', credentials)[0], 409)
        self.assertEqual(self.request('/api/logout', {}, cookie, csrf)[0], 200)
        self.assertIsNone(self.request('/api/me', cookie=cookie)[1]['user'])
        self.assertEqual(self.request('/api/login', {**credentials, 'password': 'wrong password here'})[0], 401)
        code, logged_in, cookie2 = self.request('/api/login', credentials)
        self.assertEqual(code, 200)
        self.assertEqual(logged_in['user']['bio'], 'Head nod music')
        # A new App instance reads the saved profile and session from the same database.
        reopened = App(('127.0.0.1', 0), self.db)
        with reopened.connect() as conn:
            self.assertEqual(conn.execute('SELECT bio FROM users WHERE username=?', ('test_player',)).fetchone()['bio'], 'Head nod music')
        reopened.server_close()

    def test_hidden_files_and_nonexistent_profiles(self):
        for path in ('/.git/config', '/server/app.py', '/server/../.git/config'):
            self.assertEqual(self.request(path)[0], 404)
        self.assertEqual(self.request('/api/profiles/no_such_player')[0], 404)
        self.assertEqual(self.request('/api/signup', {'username': [], 'password': 'long password'})[0], 400)

if __name__ == '__main__':
    unittest.main()
