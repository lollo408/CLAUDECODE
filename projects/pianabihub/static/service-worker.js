/**
 * Service Worker for Piana BI Hub PWA
 * Handles caching strategies, offline functionality, forced updates, and push notifications
 */

const CACHE_VERSION = 'piana-bi-v10';
const OFFLINE_URL = '/offline';

// Assets to cache immediately on install
const PRECACHE_ASSETS = [
  '/',
  '/offline',
  '/maintenance',
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

// Listen for messages from the main page
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'FORCE_UPDATE') {
    console.log('[Service Worker] Received force update command');

    // Clear all caches
    event.waitUntil(
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            console.log('[Service Worker] Clearing cache:', cacheName);
            return caches.delete(cacheName);
          })
        );
      }).then(() => {
        // Notify all clients that cache is cleared
        self.clients.matchAll().then((clients) => {
          clients.forEach((client) => {
            client.postMessage({ type: 'CACHE_CLEARED' });
          });
        });
      })
    );
  }
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
         pathname === '/maintenance' ||
         (!pathname.includes('.') && !pathname.startsWith('/api/'));
}

// --- PUSH NOTIFICATION HANDLERS ---

/**
 * Handle incoming push notifications
 */
self.addEventListener('push', (event) => {
  console.log('[Service Worker] Push received');

  let data = {
    title: 'Piana BI Hub',
    body: 'New content available',
    url: '/dashboard',
    icon: '/static/icons/icon-192.png',
    badge: '/static/icons/icon-192.png'
  };

  // Parse push data if available
  if (event.data) {
    try {
      data = { ...data, ...event.data.json() };
    } catch (e) {
      console.error('[Service Worker] Error parsing push data:', e);
    }
  }

  const options = {
    body: data.body,
    icon: data.icon || '/static/icons/icon-192.png',
    badge: data.badge || '/static/icons/icon-192.png',
    vibrate: [100, 50, 100],
    data: {
      url: data.url || '/dashboard',
      dateOfArrival: Date.now()
    },
    actions: [
      {
        action: 'open',
        title: 'View'
      },
      {
        action: 'dismiss',
        title: 'Dismiss'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

/**
 * Handle notification click
 */
self.addEventListener('notificationclick', (event) => {
  console.log('[Service Worker] Notification clicked, action:', event.action);

  event.notification.close();

  // Handle dismiss action
  if (event.action === 'dismiss') {
    return;
  }

  // Target URL from notification data
  const targetPath = event.notification.data?.url || '/dashboard';
  const targetUrl = new URL(targetPath, self.location.origin).href;

  event.waitUntil(
    // First, try to find an existing window/tab for our app
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((windowClients) => {
        // Look for any existing window on our origin
        for (const client of windowClients) {
          if (client.url.startsWith(self.location.origin)) {
            // Found an existing window - focus it and navigate
            console.log('[Service Worker] Found existing window, navigating to:', targetPath);
            return client.focus().then((focusedClient) => {
              // Navigate the existing window to target
              return focusedClient.navigate(targetUrl);
            });
          }
        }

        // No existing window found - open new one
        // Use direct URL (session cookie should be sent for same-origin)
        console.log('[Service Worker] No existing window, opening new:', targetUrl);
        return clients.openWindow(targetUrl);
      })
  );
});

/**
 * Handle notification close (for analytics if needed)
 */
self.addEventListener('notificationclose', (event) => {
  console.log('[Service Worker] Notification closed without action');
});
