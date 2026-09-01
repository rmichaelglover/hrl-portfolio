const CACHE = 'easy-bible-reader-v0.4';
const FILES = [
  './', './index.html', './style.css', './app.js?v=2',
  './data/translations.js', './data/web-canon.js?v=1'
];

self.addEventListener('install', event => event.waitUntil(
  caches.open(CACHE).then(cache => cache.addAll(FILES)).then(() => self.skipWaiting())
));
self.addEventListener('activate', event => event.waitUntil(
  caches.keys()
    .then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key))))
    .then(() => self.clients.claim())
));
self.addEventListener('fetch', event => event.respondWith(
  caches.match(event.request).then(response => response || fetch(event.request))
));
