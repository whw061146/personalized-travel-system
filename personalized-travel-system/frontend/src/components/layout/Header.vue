<template>
  <header class="app-header">
    <div class="container header-container">
      <div class="logo" @click="$router.push('/')">
        <h1>个性化旅游推荐</h1>
      </div>
      
      <el-menu
        :default-active="activeIndex"
        mode="horizontal"
        class="nav-menu"
        :ellipsis="false"
        @select="handleSelect"
      >
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/map">地图</el-menu-item>
        <el-menu-item index="/food">美食</el-menu-item>
        <el-menu-item index="/diary">旅行日记</el-menu-item>
      </el-menu>
      
      <div class="user-actions">
        <template v-if="isLoggedIn">
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-avatar">
              <el-avatar :size="32" :src="userInfo?.avatar || ''">{{ userInfo?.username?.charAt(0).toUpperCase() || 'U' }}</el-avatar>
              <span class="username">{{ userInfo?.username || '用户' }}</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="settings">设置</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <el-button type="text" @click="$router.push('/login')">登录</el-button>
          <el-button type="primary" @click="$router.push('/register')">注册</el-button>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../../store'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 计算属性获取登录状态和用户信息
const isLoggedIn = computed(() => userStore.isLoggedIn)
const userInfo = computed(() => userStore.getUserInfo)

// 当前激活的菜单项
const activeIndex = ref('/')

// 监听路由变化，更新激活的菜单项
watch(() => route.path, (newPath) => {
  activeIndex.value = newPath
})

// 菜单选择处理
const handleSelect = (key) => {
  router.push(key)
}

// 下拉菜单命令处理
const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      router.push('/profile/settings')
      break
    case 'logout':
      userStore.logout()
      ElMessage.success('已成功退出登录')
      router.push('/')
      break
  }
}

onMounted(() => {
  // 初始化激活菜单项为当前路由路径
  activeIndex.value = route.path
})
</script>

<style scoped>
.app-header {
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  padding: 0 20px;
}

.logo {
  cursor: pointer;
  display: flex;
  align-items: center;
}

.logo h1 {
  margin: 0;
  font-size: 1.5rem;
  color: #409EFF;
}

.nav-menu {
  flex: 1;
  margin: 0 20px;
  border-bottom: none;
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin-left: 8px;
  font-size: 14px;
}

@media (max-width: 768px) {
  .username {
    display: none;
  }
  
  .nav-menu {
    margin: 0 10px;
  }
  
  .logo h1 {
    font-size: 1.2rem;
  }
  
  .nav-menu {
    display: none;
  }
}
</style>