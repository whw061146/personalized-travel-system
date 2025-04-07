/**
 * 地图API集成脚本
 * 用于加载和初始化第三方地图服务
 */

// 高德地图API加载
function loadAMapAPI() {
  return new Promise((resolve, reject) => {
    // 检查是否已加载
    if (window.AMap) {
      resolve(window.AMap);
      return;
    }

    // 创建script标签
    const script = document.createElement('script');
    script.type = 'text/javascript';
    script.async = true;
    script.src = 'https://webapi.amap.com/maps?v=2.0&key=YOUR_AMAP_KEY';
    script.onerror = reject;
    script.onload = () => {
      if (window.AMap) {
        // 加载高德地图UI组件库
        const uiScript = document.createElement('script');
        uiScript.type = 'text/javascript';
        uiScript.async = true;
        uiScript.src = 'https://webapi.amap.com/ui/1.1/main.js';
        uiScript.onerror = reject;
        uiScript.onload = () => {
          resolve(window.AMap);
        };
        document.head.appendChild(uiScript);
      } else {
        reject(new Error('高德地图API加载失败'));
      }
    };
    document.head.appendChild(script);
  });
}

// 百度地图API加载
function loadBMapAPI() {
  return new Promise((resolve, reject) => {
    // 检查是否已加载
    if (window.BMap) {
      resolve(window.BMap);
      return;
    }

    // 创建script标签
    const script = document.createElement('script');
    script.type = 'text/javascript';
    script.async = true;
    script.src = 'https://api.map.baidu.com/api?v=3.0&ak=YOUR_BMAP_KEY&callback=initBMap';
    script.onerror = reject;
    
    // 定义回调函数
    window.initBMap = function() {
      if (window.BMap) {
        resolve(window.BMap);
      } else {
        reject(new Error('百度地图API加载失败'));
      }
    };
    
    document.head.appendChild(script);
  });
}

// 初始化地图
function initMap(mapType, containerId, options = {}) {
  const defaultOptions = {
    center: [116.397428, 39.90923], // 默认中心点（北京）
    zoom: 11,                      // 默认缩放级别
    showIndoorMap: true            // 显示室内地图
  };
  
  const mapOptions = { ...defaultOptions, ...options };
  
  if (mapType === 'amap') {
    return loadAMapAPI().then(AMap => {
      return new AMap.Map(containerId, {
        center: mapOptions.center,
        zoom: mapOptions.zoom,
        showIndoorMap: mapOptions.showIndoorMap
      });
    });
  } else if (mapType === 'bmap') {
    return loadBMapAPI().then(BMap => {
      const map = new BMap.Map(containerId);
      const point = new BMap.Point(mapOptions.center[0], mapOptions.center[1]);
      map.centerAndZoom(point, mapOptions.zoom);
      if (mapOptions.showIndoorMap) {
        map.addControl(new BMap.MapTypeControl());
      }
      return map;
    });
  } else {
    return Promise.reject(new Error('不支持的地图类型'));
  }
}

// 导出地图API
window.MapAPI = {
  loadAMapAPI,
  loadBMapAPI,
  initMap
};