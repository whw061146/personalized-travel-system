// 缓存名称，更新版本时需要修改此值
const CACHE_NAME = 'travel-app-v1';

// 需要缓存的资源列表
const urlsToCache = [
  '/',
  '/index.html',
  '/favicon.ico',
  '/manifest.json',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png',
  '/assets/main.css',
  '/assets/banner.jpg'
];

// 安装 Service Worker
self.addEventListener('install', event => {
  // 执行安装步骤
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('缓存已打开');
        return cache.addAll(urlsToCache);
      })
      .then(() => self.skipWaiting())
  );
});

// 激活 Service Worker
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            // 删除不在白名单中的缓存
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// 拦截请求并提供缓存响应
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // 如果找到缓存的响应，则返回缓存
        if (response) {
          return response;
        }
        
        // 克隆请求，因为请求是一个流，只能使用一次
        const fetchRequest = event.request.clone();
        
        // 发起网络请求
        return fetch(fetchRequest).then(response => {
          // 检查响应是否有效
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }
          
          // 克隆响应，因为响应是一个流，只能使用一次
          const responseToCache = response.clone();
          
          // 将响应添加到缓存
          caches.open(CACHE_NAME)
            .then(cache => {
              cache.put(event.request, responseToCache);
            });
            
          return response;
        });
      })
  );
});

// 处理推送通知
self.addEventListener('push', event => {
  const title = '个性化旅游推荐系统';
  const options = {
    body: event.data.text() || '有新的旅游推荐给您！',
    icon: '/icons/icon-192x192.png',
    badge: '/favicon.ico'
  };
  
  event.waitUntil(self.registration.showNotification(title, options));
});

// 处理通知点击
self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  event.waitUntil(
    clients.openWindow('/')
  );
});