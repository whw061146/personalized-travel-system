<template>
  <div class="sidebar" :class="{ 'collapsed': isCollapsed }">
    <div class="sidebar-header">
      <h3 v-if="!isCollapsed">{{ title }}</h3>
      <el-button 
        type="text" 
        :icon="isCollapsed ? 'el-icon-s-unfold' : 'el-icon-s-fold'" 
        @click="toggleCollapse"
        class="collapse-btn"
      />
    </div>
    
    <el-menu
      :default-active="activeMenu"
      class="sidebar-menu"
      :collapse="isCollapsed"
      :collapse-transition="false"
      @select="handleSelect"
    >
      <template v-for="(item, index) in menuItems" :key="index">
        <el-sub-menu v-if="item.children && item.children.length > 0" :index="item.path">
          <template #title>
            <i :class="item.icon"></i>
            <span>{{ item.title }}</span>
          </template>
          <el-menu-item 
            v-for="(child, childIndex) in item.children" 
            :key="childIndex" 
            :index="child.path"
          >
            <i :class="child.icon"></i>
            <span>{{ child.title }}</span>
          </el-menu-item>
        </el-sub-menu>
        
        <el-menu-item v-else :index="item.path">
          <i :class="item.icon"></i>
          <span>{{ item.title }}</span>
        </el-menu-item>
      </template>
    </el-menu>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const props = defineProps({
  title: {
    type: String,
    default: '导航菜单'
  },
  menuItems: {
    type: Array,
    default: () => []
  },
  defaultCollapsed: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select', 'collapse-change'])

const route = useRoute()
const router = useRouter()

const isCollapsed = ref(props.defaultCollapsed)
const activeMenu = ref('')

// 监听路由变化，更新激活的菜单项
watch(
  () => route.path,
  (newPath) => {
    activeMenu.value = newPath
  },
  { immediate: true }
)

// 切换折叠状态
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
  emit('collapse-change', isCollapsed.value)
}

// 菜单选择处理
const handleSelect = (key) => {
  router.push(key)
  emit('select', key)
}
</script>

<style scoped>
.sidebar {
  height: 100%;
  background-color: #fff;
  border-right: 1px solid var(--border-color);
  transition: width 0.3s;
  width: 240px;
  overflow: hidden;
}

.sidebar.collapsed {
  width: 64px;
}

.sidebar-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  border-bottom: 1px solid var(--border-color);
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.collapse-btn {
  padding: 0;
  font-size: 18px;
}

.sidebar-menu {
  border-right: none;
  height: calc(100% - 60px);
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 100%;
}
</style>