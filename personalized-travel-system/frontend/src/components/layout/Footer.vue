<template>
  <footer class="app-footer">
    <div class="container footer-container">
      <div class="footer-section">
        <h3>个性化旅游推荐系统</h3>
        <p>发现您的专属旅行体验</p>
      </div>
      
      <div class="footer-section">
        <h4>快速链接</h4>
        <ul class="footer-links">
          <li><router-link to="/">首页</router-link></li>
          <li><router-link to="/map">地图</router-link></li>
          <li><router-link to="/food">美食</router-link></li>
          <li><router-link to="/diary">旅行日记</router-link></li>
        </ul>
      </div>
      
      <div class="footer-section">
        <h4>联系我们</h4>
        <ul class="footer-links">
          <li><a href="mailto:contact@travel-system.com">contact@travel-system.com</a></li>
          <li><a href="tel:+86123456789">+86 123 456 789</a></li>
        </ul>
      </div>
      
      <div class="footer-section">
        <h4>关注我们</h4>
        <div class="social-links">
          <a href="#" title="微信"><i class="el-icon-chat-dot-round"></i></a>
          <a href="#" title="微博"><i class="el-icon-s-promotion"></i></a>
          <a href="#" title="抖音"><i class="el-icon-video-camera"></i></a>
        </div>
      </div>
    </div>
    
    <div class="footer-bottom">
      <div class="container">
        <p>&copy; {{ currentYear }} 个性化旅游推荐系统. 保留所有权利.</p>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const currentYear = ref(new Date().getFullYear())
</script>

<style scoped>
.app-footer {
  background-color: #2c3e50;
  color: #fff;
  padding-top: 40px;
  margin-top: auto;
}

.footer-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 30px;
  padding-bottom: 30px;
}

.footer-section {
  flex: 1;
  min-width: 200px;
}

.footer-section h3 {
  font-size: 18px;
  margin-bottom: 15px;
  color: #fff;
}

.footer-section h4 {
  font-size: 16px;
  margin-bottom: 15px;
  color: #fff;
}

.footer-section p {
  color: #ccc;
  margin-bottom: 15px;
}

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-links li {
  margin-bottom: 10px;
}

.footer-links a {
  color: #ccc;
  text-decoration: none;
  transition: color 0.3s;
}

.footer-links a:hover {
  color: #fff;
}

.social-links {
  display: flex;
  gap: 15px;
}

.social-links a {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.1);
  color: #fff;
  transition: background-color 0.2s ease;
}

.social-links a:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.footer-bottom {
  background-color: rgba(0, 0, 0, 0.2);
  padding: 15px 0;
  text-align: center;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-bottom p {
  margin: 0;
  font-size: 14px;
  color: #ccc;
}

@media (max-width: 768px) {
  .footer-container {
    flex-direction: column;
    gap: 20px;
  }
  
  .footer-section {
    min-width: 100%;
  }
}
</style>