const CACHE_NAME = 'amekdala-v1';
const urlsToCache = [
    '/',
    '/static/js/index.js',
    '/static/css/style.css' // (if you have one)
];

// Install the service worker and cache core files
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
    );
});

// Serve cached files when offline
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => response || fetch(event.request))
    );
});
