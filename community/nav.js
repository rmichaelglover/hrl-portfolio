'use strict';
(async () => {
  try {
    const response = await fetch('/api/me', {credentials: 'same-origin'});
    if (!response.ok || !(response.headers.get('content-type') || '').includes('application/json')) return;
    const {user} = await response.json();
    if (user) for (const link of document.querySelectorAll('[data-account-link]')) {
      link.textContent = 'My profile';
      link.href = 'community/?user=' + encodeURIComponent(user.username);
    }
  } catch { /* Chess remains available while the account service is offline. */ }
})();
