// Service worker de la PWA: permite jugar sin conexion y actualiza solo.
// Estrategia "stale-while-revalidate": sirve la version en cache al instante
// y descarga la nueva en segundo plano; al siguiente arranque ya esta actualizada.
const CACHE = 'pixel-zombies-v1';
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icons/icon-180.png',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-512-maskable.png',
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    caches.open(CACHE).then(cache =>
      cache.match(e.request).then(cached => {
        const network = fetch(e.request).then(resp => {
          if (resp && resp.status === 200 && resp.type === 'basic') cache.put(e.request, resp.clone());
          return resp;
        }).catch(() => cached);
        return cached || network;
      })
    )
  );
});
