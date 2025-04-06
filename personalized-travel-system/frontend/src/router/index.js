import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../store'

// 路由懒加载 - 提高应用性能
const Home = () => import('../views/Home.vue')
const Login = () => import('../views/Login.vue')
const Register = () => import('../views/Register.vue')
const PlaceDetail = () => import('../views/PlaceDetail.vue')
const FoodRecommend = () => import('../views/FoodRecommend.vue')
const MapView = () => import('../views/MapView.vue')
const Diary = () => import('../views/Diary.vue')
const Profile = () => import('../views/Profile.vue')
const NotFound = () => import('../views/NotFound.vue')

// 定义路由配置
const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { 
      title: '首页', 
      requiresAuth: false,
      icon: 'home',
      keepAlive: true
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { 
      title: '登录', 
      requiresAuth: false,
      icon: 'user'
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { 
      title: '注册', 
      requiresAuth: false,
      icon: 'edit'
    }
  },
  {
    path: '/place/:id',
    name: 'PlaceDetail',
    component: PlaceDetail,
    props: true,
    meta: { 
      title: '景点详情', 
      requiresAuth: false,
      icon: 'location'
    }
  },
  {
    path: '/food',
    name: 'FoodRecommend',
    component: FoodRecommend,
    meta: { 
      title: '美食推荐', 
      requiresAuth: false,
      icon: 'food',
      keepAlive: true
    }
  },
  {
    path: '/map',
    name: 'MapView',
    component: MapView,
    meta: { 
      title: '地图', 
      requiresAuth: false,
      icon: 'map',
      keepAlive: true
    }
  },
  {
    path: '/diary',
    name: 'Diary',
    component: Diary,
    meta: { 
      title: '旅游日记', 
      requiresAuth: true,
      icon: 'notebook'
    },
    children: [
      {
        path: 'create',
        name: 'CreateDiary',
        component: () => import('../views/CreateDiary.vue'),
        meta: { 
          title: '创建日记', 
          requiresAuth: true,
          icon: 'edit'
        }
      },
      {
        path: 'edit/:id',
        name: 'EditDiary',
        component: () => import('../views/EditDiary.vue'),
        props: true,
        meta: { 
          title: '编辑日记', 
          requiresAuth: true,
          icon: 'edit'
        }
      }
    ]
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { 
      title: '个人中心', 
      requiresAuth: true,
      icon: 'user'
    },
    children: [
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('../views/Settings.vue'),
        meta: { 
          title: '账户设置', 
          requiresAuth: true,
          icon: 'setting'
        }
      },
      {
        path: 'favorites',
        name: 'Favorites',
        component: () => import('../views/Favorites.vue'),
        meta: { 
          title: '我的收藏', 
          requiresAuth: true,
          icon: 'star'
        }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: { 
      title: '页面不存在', 
      requiresAuth: false,
      icon: 'warning'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  // 滚动行为控制
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title} - 个性化旅游推荐系统`
  
  // 获取用户状态
  const userStore = useUserStore()
  const isAuthenticated = userStore.isLoggedIn
  
  // 检查是否需要登录权限
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ 
      name: 'Login', 
      query: { redirect: to.fullPath },
      // 保存尝试访问的位置，以便登录后重定向
      params: { loginRequired: true }
    })
  } else {
    // 如果已登录且尝试访问登录/注册页，重定向到首页
    if (isAuthenticated && (to.name === 'Login' || to.name === 'Register')) {
      next({ name: 'Home' })
    } else {
      next()
    }
  }
})

// 全局后置钩子
router.afterEach((to, from) => {
  // 可以在这里添加分析代码
  console.log(`页面跳转从 ${from.name || '未知页面'} 到 ${to.name}`)
  
  // 可以在这里添加页面访问统计
  if (window.gtag) {
    window.gtag('config', 'UA-XXXXXXXX-X', {
      'page_path': to.fullPath
    })
  }
})

export default router