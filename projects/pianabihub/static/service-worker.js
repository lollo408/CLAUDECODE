/**
 * Service Worker for Piana BI Hub PWA
 * Handles caching strategies and offline functionality
 */

const CACHE_VERSION = 'piana-bi-v1';
const OFFLINE_URL = '/offline';

// Assets to cache immediately on install
const PRECACHE_ASSETS = [
  '/',
  '/offline',
  '/static/css/base.css',
  '/static/css/components.css',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
  '/static/manifest.json'
];

// Install event: Pre-cache essential assets
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');

  event.waitUntil(
    caches.open(CACHE_VERSION)
      .then((cache) => {
        console.log('[Service Worker] Pre-caching offline page and assets');
        return cache.addAll(PRECACHE_ASSETS);
      })
      .then(() => self.skipWaiting()) // Activate immediately
  );
});

// Activate event: Clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...');

  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_VERSION) {
              console.log('[Service Worker] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => self.clients.claim()) // Take control immediately
  );
});

// Fetch event: Implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Skip API calls (always use network for dynamic data)
  if (url.pathname.startsWith('/api/')) {
    return;
  }

  // Strategy 1: Cache-first for static assets (CSS, JS, images, icons)
  if (isStaticAsset(url.pathname)) {
    event.respondWith(cacheFirst(request));
    return;
  }

  // Strategy 2: Network-first for HTML pages (fresh content preferred)
  if (isHTMLPage(url.pathname)) {
    event.respondWith(networkFirst(request));
    return;
  }

  // Default: Network-first
  event.respondWith(networkFirst(request));
});

/**
 * Cache-first strategy: Serve from cache, fallback to network
 * Best for static assets that rarely change
 */
async function cacheFirst(request) {
  const cache = await caches.open(CACHE_VERSION);
  const cached = await cache.match(request);

  if (cached) {
    console.log('[Service Worker] Serving from cache:', request.url);
    return cached;
  }

  try {
    const response = await fetch(request);

    // Cache successful responses
    if (response.status === 200) {
      cache.put(request, response.clone());
    }

    return response;
  } catch (error) {
    console.error('[Service Worker] Cache-first fetch failed:', error);
    throw error;
  }
}

/**
 * Network-first strategy: Try network, fallback to cache
 * Best for HTML pages that should be fresh but work offline
 */
async function networkFirst(request) {
  const cache = await caches.open(CACHE_VERSION);

  try {
    const response = await fetch(request);

    // Cache successful HTML responses
    if (response.status === 200) {
      cache.put(request, response.clone());
    }

    return response;
  } catch (error) {
    console.log('[Service Worker] Network failed, trying cache:', request.url);

    const cached = await cache.match(request);

    if (cached) {
      return cached;
    }

    // If no cache, show offline page
    if (isHTMLPage(new URL(request.url).pathname)) {
      const offlineResponse = await cache.match(OFFLINE_URL);
      if (offlineResponse) {
        return offlineResponse;
      }
    }

    throw error;
  }
}

/**
 * Check if pathname is a static asset
 */
function isStaticAsset(pathname) {
  const staticExtensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.svg', '.gif', '.woff', '.woff2', '.ttf'];
  return staticExtensions.some(ext => pathname.endsWith(ext)) || pathname.includes('/static/');
}

/**
 * Check if pathname is an HTML page
 */
function isHTMLPage(pathname) {
  // Root path or paths without extensions are HTML pages
  return pathname === '/' ||
         pathname.startsWith('/dashboard') ||
         pathname.startsWith('/events') ||
         pathname.startsWith('/archive') ||
         pathname.startsWith('/home') ||
         pathname === '/offline' ||
         (!pathname.includes('.') && !pathname.startsWith('/api/'));
}
