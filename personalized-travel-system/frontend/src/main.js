import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import pinia from './store'
import './assets/main.css'

// 创建Vue应用实例
const app = createApp(App)

// 注册全局组件和插件
app.use(ElementPlus)
app.use(router)
app.use(pinia)

// 配置全局错误处理
app.config.errorHandler = (err, vm, info) => {
  console.error('全局错误:', err)
  console.error('错误信息:', info)
  // 可以在这里添加错误上报逻辑
  // 例如发送到后端API或第三方监控服务
}

// 添加全局属性
app.config.globalProperties.$filters = {
  formatDate(value) {
    if (!value) return ''
    return new Date(value).toLocaleString()
  }
}

// 挂载应用到DOM
app.mount('#app')

// 添加错误上报逻辑
const reportError = (error, info) => {
  // 这里可以实现向后端API发送错误信息的逻辑
  // 例如使用axios发送POST请求
  console.log('错误已上报:', error, info)
}

// 注册错误上报函数
app.config.errorHandler = (err, vm, info) => {
  console.error('全局错误:', err)
  console.error('错误信息:', info)
  // 调用错误上报函数
  reportError(err, info)
}

console.log('应用已启动')