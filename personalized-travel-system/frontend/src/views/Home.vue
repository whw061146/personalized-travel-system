<template>
  <div class="home-container">
    <div class="banner">
      <h1>个性化旅游推荐系统</h1>
      <p>发现您的专属旅行体验</p>
    </div>
    
    <div class="features container">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8">
          <el-card class="feature-card">
            <template #header>
              <div class="card-header">
                <i class="el-icon-location"></i>
                <span>景点推荐</span>
              </div>
            </template>
            <div class="card-content">
              <p>基于您的偏好，为您推荐最适合的旅游景点</p>
              <el-button type="primary" @click="$router.push('/map')">探索景点</el-button>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :md="8">
          <el-card class="feature-card">
            <template #header>
              <div class="card-header">
                <i class="el-icon-food"></i>
                <span>美食发现</span>
              </div>
            </template>
            <div class="card-content">
              <p>发现当地特色美食，满足您的味蕾体验</p>
              <el-button type="primary" @click="$router.push('/food')">寻找美食</el-button>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :md="8">
          <el-card class="feature-card">
            <template #header>
              <div class="card-header">
                <i class="el-icon-notebook"></i>
                <span>旅行日记</span>
              </div>
            </template>
            <div class="card-content">
              <p>记录您的旅行点滴，分享精彩瞬间</p>
              <el-button type="primary" @click="$router.push('/diary')">开始记录</el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
// 首页组件逻辑
</script>

<style scoped>
.home-container {
  width: 100%;
}

.banner {
  height: 400px;
  background-image: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url('@/assets/banner.jpg');
  background-size: cover;
  background-position: center;
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  margin-bottom: 40px;
}

.banner h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.banner p {
  font-size: 1.2rem;
}

.features {
  padding: 20px 0 40px;
}

.feature-card {
  height: 100%;
  margin-bottom: 20px;
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.card-header {
  display: flex;
  align-items: center;
  font-size: 18px;
}

.card-header i {
  margin-right: 10px;
}

.card-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.card-content p {
  margin-bottom: 15px;
  color: var(--text-regular);
}

@media screen and (max-width: 768px) {
  .banner {
    height: 300px;
  }
  
  .banner h1 {
    font-size: 2rem;
  }
}
</style>