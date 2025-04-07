<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="profile-header">
          <h2>个人中心</h2>
        </div>
      </template>
      
      <div class="user-info" v-if="userInfo">
        <div class="avatar-container">
          <el-avatar :size="100" :src="userInfo.avatar">
            {{ userInfo.username ? userInfo.username.charAt(0).toUpperCase() : 'U' }}
          </el-avatar>
        </div>
        
        <div class="user-details">
          <h3>{{ userInfo.username }}</h3>
          <p><i class="el-icon-message"></i> {{ userInfo.email }}</p>
          <p v-if="userInfo.phone"><i class="el-icon-phone"></i> {{ userInfo.phone }}</p>
          <p v-if="userInfo.location"><i class="el-icon-location"></i> {{ userInfo.location }}</p>
        </div>
      </div>
      
      <div class="profile-actions">
        <el-button type="primary" @click="$router.push('/profile/settings')">
          <i class="el-icon-setting"></i> 账户设置
        </el-button>
        <el-button type="success" @click="$router.push('/profile/favorites')">
          <i class="el-icon-star-on"></i> 我的收藏
        </el-button>
        <el-button type="info" @click="$router.push('/diary')">
          <i class="el-icon-notebook-1"></i> 我的日记
        </el-button>
      </div>
    </el-card>
    
    <!-- 子路由视图 -->
    <router-view></router-view>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useUserStore } from '../store'

// 用户状态管理
const userStore = useUserStore()

// 获取用户信息
const userInfo = computed(() => userStore.getUserInfo)

// 如果用户未登录，重定向到登录页面
if (!userStore.isLoggedIn) {
  router.push('/login')
}
</script>

<style scoped lang="scss">
.profile-container {
  max-width: 1200px;
  margin: 20px auto;
  padding: 0 20px;
}

.profile-card {
  margin-bottom: 30px;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  
  @media (max-width: 768px) {
    flex-direction: column;
    text-align: center;
  }
}

.avatar-container {
  margin-right: 30px;
  
  @media (max-width: 768px) {
    margin-right: 0;
    margin-bottom: 20px;
  }
}

.user-details {
  h3 {
    margin-top: 0;
    margin-bottom: 10px;
    font-size: 1.5rem;
  }
  
  p {
    margin: 5px 0;
    color: #606266;
    
    i {
      margin-right: 8px;
    }
  }
}

.profile-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  
  @media (max-width: 768px) {
    justify-content: center;
  }
}
</style>