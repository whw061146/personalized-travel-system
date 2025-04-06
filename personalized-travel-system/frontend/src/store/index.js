import { createPinia, defineStore } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

// 创建pinia实例
const pinia = createPinia()

// 使用持久化插件
pinia.use(piniaPluginPersistedstate)

// 用户状态
export const useUserStore = defineStore('user', {
  state: () => ({
    token: null,
    userInfo: null,
    preferences: {
      travelTypes: [],
      foodPreferences: [],
      budgetRange: null
    }
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
    getUserInfo: (state) => state.userInfo,
    getUserPreferences: (state) => state.preferences
  },
  actions: {
    setToken(token) {
      this.token = token
    },
    setUserInfo(userInfo) {
      this.userInfo = userInfo
    },
    setPreferences(preferences) {
      this.preferences = preferences
    },
    logout() {
      this.token = null
      this.userInfo = null
    }
  },
  persist: {
    key: 'user-store',
    storage: localStorage
  }
})

// 推荐状态
export const useRecommendStore = defineStore('recommend', {
  state: () => ({
    recentPlaces: [],
    recentFoods: [],
    searchHistory: []
  }),
  actions: {
    addRecentPlace(place) {
      // 避免重复添加
      if (!this.recentPlaces.some(p => p.id === place.id)) {
        this.recentPlaces.unshift(place)
        // 最多保存10条记录
        if (this.recentPlaces.length > 10) {
          this.recentPlaces.pop()
        }
      }
    },
    addRecentFood(food) {
      if (!this.recentFoods.some(f => f.id === food.id)) {
        this.recentFoods.unshift(food)
        if (this.recentFoods.length > 10) {
          this.recentFoods.pop()
        }
      }
    },
    addSearchHistory(keyword) {
      if (keyword && !this.searchHistory.includes(keyword)) {
        this.searchHistory.unshift(keyword)
        if (this.searchHistory.length > 20) {
          this.searchHistory.pop()
        }
      }
    },
    clearSearchHistory() {
      this.searchHistory = []
    }
  },
  persist: {
    key: 'recommend-store',
    storage: localStorage
  }
})

// 系统设置状态
export const useSettingsStore = defineStore('settings', {
  state: () => ({
    theme: 'light',
    language: 'zh-CN',
    mapSettings: {
      defaultZoom: 12,
      defaultCenter: { lat: 39.9042, lng: 116.4074 }, // 默认北京
      showTraffic: false
    },
    notification: {
      enabled: true,
      sound: true,
      vibration: true
    },
    displaySettings: {
      listViewMode: 'card', // 'card' 或 'list'
      resultsPerPage: 10,
      showImages: true
    }
  }),
  getters: {
    isDarkMode: (state) => state.theme === 'dark',
    getMapSettings: (state) => state.mapSettings,
    getNotificationSettings: (state) => state.notification
  },
  actions: {
    toggleTheme() {
      this.theme = this.theme === 'light' ? 'dark' : 'light'
      // 应用主题到DOM
      document.documentElement.setAttribute('data-theme', this.theme)
    },
    setLanguage(lang) {
      this.language = lang
    },
    updateMapSettings(settings) {
      this.mapSettings = { ...this.mapSettings, ...settings }
    },
    updateNotificationSettings(settings) {
      this.notification = { ...this.notification, ...settings }
    },
    updateDisplaySettings(settings) {
      this.displaySettings = { ...this.displaySettings, ...settings }
    },
    resetSettings() {
      this.$reset()
    }
  },
  persist: {
    key: 'settings-store',
    storage: localStorage
  }
})

export default pinia