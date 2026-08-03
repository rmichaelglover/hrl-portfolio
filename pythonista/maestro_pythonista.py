"""Run Chess Maestro inside Pythonista on iPhone or iPad.

Copy the entire ``whimsy-chess`` folder into Pythonista (typically through the
Files app), then run this script.  A loopback HTTP server is used instead of a
``file:`` URL so Maestro's relative JavaScript assets load consistently in
WKWebView.

This file intentionally depends only on Pythonista's bundled modules and the
Python standard library.
"""

from __future__ import annotations

from functools import partial
import http.server
import base64
import json
from pathlib import Path
import socketserver
import threading
import tempfile
import urllib.parse

import console
import dialogs
import ui


APP_ROOT = Path(__file__).resolve().parent.parent
MAESTRO_FILE = APP_ROOT / "maestro.html"


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """Serve Maestro locally without filling Pythonista's console."""

    def log_message(self, _format, *args):
        pass

    def end_headers(self):
        # Maestro is entirely local; prevent stale files while authoring on-device.
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()


class LocalServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


class MaestroDelegate:
    def __init__(self, app):
        self.app = app

    def webview_did_finish_load(self, webview):
        self.app.status.text = "Maestro ready"

    def webview_should_start_load(self, webview, url, navigation_type):
        """Keep portfolio links from unexpectedly replacing the application."""
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme == "chessmaestro":
            self.app.receive_export(parsed)
            return False
        if parsed.scheme in ("http", "https") and parsed.hostname not in (
            "127.0.0.1",
            "localhost",
        ):
            self.app.status.text = "External links require an internet connection"
            return False
        return True


class MaestroApp(ui.View):
    def __init__(self):
        super().__init__()
        self.name = "Chess Maestro"
        self.background_color = "#e8e6e3"
        self.exports = {}

        handler = partial(QuietHandler, directory=str(APP_ROOT))
        self.server = LocalServer(("127.0.0.1", 0), handler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

        self.web = ui.WebView(frame=self.bounds, flex="WH")
        self.web.scales_page_to_fit = False
        self.web.delegate = MaestroDelegate(self)
        self.add_subview(self.web)

        self.status = ui.Label(
            frame=(8, 4, 260, 24),
            flex="W",
            text="Loading Maestro…",
            font=("<System>", 12),
            text_color="#66615d",
            background_color=(1, 1, 1, 0.88),
        )
        self.status.corner_radius = 5
        self.status.alignment = ui.ALIGN_CENTER
        self.add_subview(self.status)

        self.right_button_items = [
            ui.ButtonItem(title="Import PGN", action=self.import_pgn),
            ui.ButtonItem(title="Reload", action=self.reload_maestro),
        ]
        self.reload_maestro()

    @property
    def url(self):
        port = self.server.server_address[1]
        return f"http://127.0.0.1:{port}/maestro.html?pythonista=1"

    def reload_maestro(self, _sender=None):
        self.status.text = "Loading Maestro…"
        self.web.load_url(self.url)

    def import_pgn(self, _sender=None):
        """Select a PGN through iOS Files and place it in Maestro's Load panel."""
        try:
            path = dialogs.pick_document(types=["public.text", "public.data"])
        except TypeError:
            # Older Pythonista builds expose pick_document without ``types``.
            path = dialogs.pick_document()
        if not path:
            return
        try:
            pgn = Path(path).read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            self.status.text = f"Could not read PGN: {exc}"
            return

        # json.dumps is the safe way to embed arbitrary PGN text in JavaScript.
        payload = json.dumps(pgn)
        filename = json.dumps(Path(path).name)
        script = f"""
        (function() {{
          var panel = document.getElementById('loadPanel');
          var text = document.getElementById('pgnText');
          if (!panel || !text) return 'Maestro load controls not found';
          panel.style.display = 'block';
          text.value = {payload};
          text.dispatchEvent(new Event('input', {{bubbles:true}}));
          panel.scrollIntoView({{behavior:'smooth', block:'start'}});
          return 'Imported ' + {filename};
        }})()
        """
        message = self.web.eval_js(script)
        self.status.text = message or f"Imported {Path(path).name}"

    @staticmethod
    def _safe_export_name(name):
        """Keep a browser-supplied filename inside the export directory."""
        cleaned = Path(name).name.replace("\x00", "").strip()
        return cleaned or "chess-maestro-export.bin"

    def receive_export(self, parsed):
        """Reassemble one export delivered through ordered, small custom URLs."""
        query = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
        get = lambda key, default="": query.get(key, [default])[0]
        action = parsed.path.strip("/")
        token = get("token")
        if not token:
            self.status.text = "Rejected an export without a transfer token"
            return

        if action == "start":
            try:
                expected = max(0, int(get("size", "0")))
            except ValueError:
                expected = 0
            self.exports[token] = {
                "name": self._safe_export_name(get("name")),
                "type": get("type", "application/octet-stream"),
                "expected": expected,
                "next": 0,
                "data": bytearray(),
            }
            self.status.text = f"Receiving {self.exports[token]['name']}…"
            return

        transfer = self.exports.get(token)
        if transfer is None:
            self.status.text = "Export transfer expired—please try again"
            return
        if action == "cancel":
            self.exports.pop(token, None)
            self.status.text = get("message", "Export cancelled")
            return
        if action == "chunk":
            try:
                index = int(get("index", "-1"))
                if index != transfer["next"]:
                    raise ValueError(f"expected chunk {transfer['next']}, got {index}")
                encoded = get("data")
                encoded += "=" * (-len(encoded) % 4)
                transfer["data"].extend(base64.urlsafe_b64decode(encoded))
                transfer["next"] += 1
                if transfer["expected"]:
                    percent = min(100, len(transfer["data"]) * 100 // transfer["expected"])
                    self.status.text = f"Receiving {transfer['name']}… {percent}%"
            except (ValueError, TypeError, base64.binascii.Error) as exc:
                self.exports.pop(token, None)
                self.status.text = f"Export transfer failed: {exc}"
            return
        if action == "end":
            self.exports.pop(token, None)
            data = bytes(transfer["data"])
            if len(data) != transfer["expected"]:
                self.status.text = (
                    f"Export incomplete: received {len(data)} of {transfer['expected']} bytes"
                )
                return
            folder = Path(tempfile.gettempdir()) / "chess-maestro-exports"
            folder.mkdir(parents=True, exist_ok=True)
            destination = folder / transfer["name"]
            if destination.exists():
                stem, suffix = destination.stem, destination.suffix
                number = 2
                while destination.exists():
                    destination = folder / f"{stem}-{number}{suffix}"
                    number += 1
            destination.write_bytes(data)
            self.status.text = f"Ready to share {destination.name}"
            console.open_in(str(destination))

    def will_close(self):
        # shutdown() can wait for the server loop, so never block the UI thread.
        threading.Thread(target=self.server.shutdown, daemon=True).start()


def main():
    if not MAESTRO_FILE.exists():
        raise FileNotFoundError(
            "maestro.html was not found. Copy the complete whimsy-chess folder "
            "into Pythonista, preserving the pythonista subfolder."
        )
    app = MaestroApp()
    app.present("fullscreen", hide_title_bar=False, orientations=["portrait", "landscape"])


if __name__ == "__main__":
    main()
