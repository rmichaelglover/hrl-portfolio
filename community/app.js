'use strict';
const $ = id => document.getElementById(id);
const params = new URLSearchParams(location.search);
let me = null, csrf = '', mode = 'signup', profiles = [], currentProfile = null;
const COLORS = ['#37e6ff', '#c060ff', '#5fe3a0', '#e8c170', '#ff94bf'];
function status(message) { $('status').textContent = message; }
function node(tag, text, className) { const el = document.createElement(tag); if (text != null) el.textContent = text; if (className) el.className = className; return el; }
function link(label, href, className) { const el = node('a', label, className); el.href = href; return el; }
async function api(path, data) {
  const response = await fetch('/api/' + path, { credentials: 'same-origin', headers: data ? {'Content-Type':'application/json', 'X-CSRF-Token': csrf} : {}, ...(data ? {method:'POST', body: JSON.stringify(data)} : {}) });
  const type = response.headers.get('content-type') || '';
  if (!type.includes('application/json')) throw new Error('Community service unavailable.');
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'Request failed.');
  return result;
}
function accountNav() {
  $('account-nav').textContent = me ? 'My profile' : 'Sign up / Log in';
  $('account-nav').href = me ? '?user=' + encodeURIComponent(me.username) : '?view=signup';
  $('join').hidden = !!me;
}
function setMode(next) {
  mode = next;
  $('auth-title').textContent = mode === 'signup' ? 'Create your player profile' : 'Welcome back';
  $('auth-submit').textContent = mode === 'signup' ? 'Create account' : 'Log in';
  $('password').autocomplete = mode === 'signup' ? 'new-password' : 'current-password';
  for (const name of ['signup', 'login']) {
    $(name + '-tab').classList.toggle('active', name === mode);
    $(name + '-tab').setAttribute('aria-pressed', String(name === mode));
  }
}
function profileCard(profile) {
  const card = link('', '?user=' + encodeURIComponent(profile.username), 'player');
  card.style.setProperty('--accent', COLORS.includes(profile.accent) ? profile.accent : COLORS[0]);
  card.append(node('div', profile.avatar, 'avatar'), node('h3', profile.display_name), node('div', '@' + profile.username, 'username'), node('p', profile.chess || profile.music || 'New to the Maestro community.'));
  return card;
}
function renderDirectory() {
  const term = $('search').value.toLowerCase();
  const matches = profiles.filter(p => [p.username, p.display_name, p.chess, p.music].some(value => value.toLowerCase().includes(term)));
  $('players').replaceChildren(...matches.map(profileCard));
  $('empty').hidden = !!matches.length;
  $('empty').textContent = profiles.length ? 'No matching players.' : 'No players yet. Be the first to make a profile.';
}
function renderProfile(profile) {
  currentProfile = profile;
  const panel = $('profile'); panel.replaceChildren(); panel.hidden = false;
  panel.style.setProperty('--accent', COLORS.includes(profile.accent) ? profile.accent : COLORS[0]);
  const head = node('div', null, 'profile-head'), title = node('div');
  title.append(node('h1', profile.display_name), node('div', '@' + profile.username, 'username'));
  head.append(node('div', profile.avatar, 'avatar'), title);
  panel.append(head, node('p', 'Joined ' + new Date(profile.created_at).toLocaleDateString(undefined, {year:'numeric', month:'long', day:'numeric'})), node('p', profile.bio || 'This player hasn’t added an introduction yet.', 'bio'));
  for (const [key, label] of [['chess', 'Chess interests'], ['music', 'Music room']]) {
    panel.append(node('h2', label), node('p', profile[key] || 'Still choosing favorites.', 'bio'));
  }
  const external = node('div', null, 'external-links');
  for (const [key, base, label] of [['lichess','https://lichess.org/@/','Lichess'], ['chesscom','https://www.chess.com/member/','Chess.com']]) {
    if (profile[key]) { const a = link(label + ' ↗', base + encodeURIComponent(profile[key])); a.target = '_blank'; a.rel = 'noopener noreferrer'; external.append(a); }
  }
  panel.append(external);
  const actions = node('div', null, 'profile-actions');
  actions.append(link('Play Maestro →', '../maestro.html?play=1', 'button'));
  const copy = node('button', 'Copy profile link'); copy.type = 'button';
  copy.onclick = async () => { try { await navigator.clipboard.writeText(new URL('?user=' + encodeURIComponent(profile.username), location.href).href); status('Profile link copied.'); } catch { status('Copy the profile URL from your address bar.'); } }; actions.append(copy);
  if (me && me.username === profile.username) {
    const edit = node('button', 'Edit profile'); edit.type = 'button'; edit.onclick = editProfile;
    const logout = node('button', 'Log out'); logout.type = 'button';
    logout.onclick = async () => { try { await api('logout', {}); me = null; csrf = ''; $('editor').hidden = true; accountNav(); renderProfile(profile); status('Logged out.'); } catch (error) { status(error.message); } };
    actions.append(edit, logout);
  }
  panel.append(actions);
  document.title = profile.display_name + ' (@' + profile.username + ') | Maestro';
}
function editProfile() {
  for (const field of $('edit-form').elements) if (field.name) field.value = me[field.name] || '';
  $('editor').hidden = false; $('edit-form').elements.display_name.focus();
}
$('signup-tab').onclick = () => setMode('signup');
$('login-tab').onclick = () => setMode('login');
$('cancel-edit').onclick = () => { $('editor').hidden = true; };
$('search').oninput = renderDirectory;
$('auth-form').onsubmit = async event => {
  event.preventDefault(); $('auth-submit').disabled = true; status('Connecting…');
  try {
    const result = await api(mode, Object.fromEntries(new FormData(event.target)));
    me = result.user; csrf = result.csrf; event.target.reset(); $('account').hidden = true;
    history.replaceState(null, '', '?user=' + encodeURIComponent(me.username)); accountNav(); renderProfile(me);
    if (mode === 'signup') { editProfile(); status('Your account is ready. Make your profile your own.'); } else status('Welcome back.');
  } catch (error) { status(error.message); } finally { $('auth-submit').disabled = false; }
};
$('edit-form').onsubmit = async event => {
  event.preventDefault(); const button = event.target.querySelector('button'); button.disabled = true;
  try { const result = await api('profile', Object.fromEntries(new FormData(event.target))); me = result.user; $('editor').hidden = true; renderProfile(me); status('Profile saved.'); }
  catch (error) { status(error.message); } finally { button.disabled = false; }
};
(async function init() {
  try {
    const result = await api('me'); me = result.user; csrf = result.csrf || ''; accountNav();
  } catch { $('offline').hidden = false; return; }
  if (params.get('user')) {
    try { const result = await api('profiles/' + encodeURIComponent(params.get('user'))); renderProfile(result.profile); } catch (error) { status(error.message); }
  } else if (me && params.has('view')) {
    history.replaceState(null, '', '?user=' + encodeURIComponent(me.username)); renderProfile(me);
  } else {
    $('account').hidden = !params.has('view');
    setMode(params.get('view') === 'login' ? 'login' : 'signup');
    $('directory').hidden = false;
    try { profiles = (await api('profiles')).profiles; renderDirectory(); } catch (error) { status(error.message); }
  }
})();
