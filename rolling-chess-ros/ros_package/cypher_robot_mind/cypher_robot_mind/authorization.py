"""Authenticated, expiring simulation commands; replay protected per launch."""
import hashlib
import hmac
import json
import secrets
import time

ACTIONS = {'start', 'stop', 'shutdown', 'sleep', 'wake', 'present', 'reset', 'disturb'}
PUBLIC_ACTIONS = {'stop', 'shutdown'}
BASIC_ACTIONS = PUBLIC_ACTIONS | {'sleep', 'wake', 'present'}
ADMIN_ACTIONS = ACTIONS


def permitted(role, action):
    return action in {'public':PUBLIC_ACTIONS,'basic':BASIC_ACTIONS,'admin':ADMIN_ACTIONS}.get(role,set())


class PresencePolicy:
    """Voice-evidence lease, task cancellation, and simulated power states."""
    def __init__(self, now, presence_timeout=30., sleep_timeout=900.):
        self.presence_timeout=presence_timeout; self.sleep_timeout=sleep_timeout
        self.last_presence=now; self.sleep_since=None
        self.mode='WAITING'; self.mission_until=0.
        self.reason='Waiting for an authorized voice command.'

    def apply(self, action, now):
        if action in {'stop','shutdown','sleep'}:
            self.mission_until=0.
            self.mode='HIBERNATING' if action=='shutdown' else 'SLEEPING'
            self.sleep_since=now
            self.reason='Shutdown requested.' if action=='shutdown' else 'Task stopped; mission permission cancelled.'
        elif action in {'wake','present','start'}:
            self.last_presence=now
            if action=='start':
                self.mode='RUNNING'; self.mission_until=now+90.; self.sleep_since=None
                self.reason='Authorized goal mission; 90-second limit; voice presence required.'
            elif action=='wake':
                self.mode='WAITING'; self.mission_until=0.; self.sleep_since=None
                self.reason='Awake. A new authorized start is required.'
            else:
                self.reason='Voice presence renewed; task permissions unchanged.'

    def tick(self,now):
        if self.mode in {'WAITING','RUNNING'} and now-self.last_presence>self.presence_timeout:
            self.mode='SLEEPING'; self.sleep_since=now; self.mission_until=0.
            self.reason='Voice presence expired. Task stopped and permission cancelled.'
        if self.mode=='RUNNING' and now>=self.mission_until:
            self.mode='WAITING'; self.mission_until=0.; self.reason='Mission permission expired.'
        if self.mode=='SLEEPING' and now-self.sleep_since>=self.sleep_timeout:
            self.mode='HIBERNATING'; self.reason='No wake command during 15-minute sleep; simulated hibernation.'
        return self.mode


def sign(secret, action, now=None):
    if action not in ACTIONS:
        raise ValueError('Unknown action')
    payload={'action':action,'issued':time.time() if now is None else now,'nonce':secrets.token_hex(16)}
    body=json.dumps(payload,sort_keys=True,separators=(',',':'))
    signature=hmac.new(secret.encode(),body.encode(),hashlib.sha256).hexdigest()
    return json.dumps({'payload':payload,'signature':signature})


class CommandGate:
    def __init__(self,secret):
        if not secret or len(secret)<32:
            raise ValueError('Launch-generated command secret is required')
        self.secret=secret
        self.seen={}

    def verify(self,message,now=None):
        now=time.time() if now is None else now
        try:
            envelope=json.loads(message); payload=envelope['payload']
            body=json.dumps(payload,sort_keys=True,separators=(',',':'))
            expected=hmac.new(self.secret.encode(),body.encode(),hashlib.sha256).hexdigest()
            if not hmac.compare_digest(expected,envelope['signature']): return None
            if abs(now-float(payload['issued']))>5: return None
            self.seen={nonce:t for nonce,t in self.seen.items() if now-t<10}
            nonce=payload['nonce']
            if not isinstance(nonce,str) or len(nonce)!=32 or nonce in self.seen: return None
            if payload['action'] not in ACTIONS: return None
            self.seen[nonce]=now
            return payload['action']
        except (ValueError,KeyError,TypeError):
            return None
