<template>
    <div class="login-container">
      <div class="login-card">
        <div class="login-header">
          <h2>登录</h2>
          <p>欢迎回来，请登录您的账号</p>
        </div>
        
        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          label-position="top"
          @submit.prevent="handleLogin"
        >
          <el-form-item label="用户名/邮箱" prop="username">
            <el-input 
              v-model="loginForm.username" 
              placeholder="请输入用户名或邮箱"
              prefix-icon="el-icon-user"
            />
          </el-form-item>
          
          <el-form-item label="密码" prop="password">
            <el-input 
              v-model="loginForm.password" 
              type="password" 
              placeholder="请输入密码"
              prefix-icon="el-icon-lock"
              show-password
            />
          </el-form-item>
          
          <div class="form-actions">
            <el-checkbox v-model="rememberMe">记住我</el-checkbox>
            <el-button type="text" @click="forgotPassword">忘记密码?</el-button>
          </div>
          
          <el-form-item>
            <el-button 
              type="primary" 
              native-type="submit" 
              :loading="loading" 
              class="login-button"
            >
              登录
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="login-footer">
          <p>还没有账号? <router-link to="/register">立即注册</router-link></p>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import { useUserStore } from '../store'
  
  // 路由实例
  const router = useRouter()
  const route = useRoute()
  
  // 用户状态管理
  const userStore = useUserStore()
  
  // 表单引用
  const loginFormRef = ref(null)
  
  // 加载状态
  const loading = ref(false)
  
  // 记住我选项
  const rememberMe = ref(false)
  
  // 登录表单数据
  const loginForm = reactive({
    username: '',
    password: ''
  })
  
  // 表单验证规则
  const loginRules = {
    username: [
      { required: true, message: '请输入用户名或邮箱', trigger: 'blur' },
      { min: 3, max: 50, message: '长度在3到50个字符之间', trigger: 'blur' }
    ],
    password: [
      { required: true, message: '请输入密码', trigger: 'blur' },
      { min: 6, max: 20, message: '长度在6到20个字符之间', trigger: 'blur' }
    ]
  }
  
  // 登录处理函数
  const handleLogin = async () => {
    if (!loginFormRef.value) return
    
    await loginFormRef.value.validate(async (valid) => {
      if (valid) {
        try {
          loading.value = true
          
          // 调用登录API
          const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              username: loginForm.username,
              password: loginForm.password,
              remember_me: rememberMe.value
            })
          })
          
          const data = await response.json()
          
          if (response.ok) {
            // 登录成功，保存token和用户信息
            userStore.setToken(data.token)
            userStore.setUserInfo(data.user)
            
            ElMessage.success('登录成功')
            
            // 如果有重定向地址，则跳转到该地址，否则跳转到首页
            const redirectPath = route.query.redirect || '/'
            router.push(redirectPath)
          } else {
            ElMessage.error(data.message || '登录失败，请检查用户名和密码')
          }
        } catch (error) {
          console.error('登录错误:', error)
          ElMessage.error('登录过程中发生错误，请稍后再试')
        } finally {
          loading.value = false
        }
      }
    })
  }
  
  // 忘记密码处理函数
  const forgotPassword = () => {
    ElMessage.info('密码重置功能即将上线，请联系管理员重置密码')
  }
  </script>
  
  <style scoped>
  .login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: calc(100vh - 120px); /* 减去header和footer的高度 */
    background-color: #f5f7fa;
    padding: 20px;
  }
  
  .login-card {
    width: 100%;
    max-width: 400px;
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    padding: 30px;
  }
  
  .login-header {
    text-align: center;
    margin-bottom: 30px;
  }
  
  .login-header h2 {
    font-size: 24px;
    color: #303133;
    margin-bottom: 10px;
  }
  
  .login-header p {
    color: #909399;
    font-size: 14px;
  }
  
  .form-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }
  
  .login-button {
    width: 100%;
    padding: 12px 0;
    font-size: 16px;
  }
  
  .login-footer {
    text-align: center;
    margin-top: 20px;
    color: #606266;
  }
  
  .login-footer a {
    color: #409EFF;
    text-decoration: none;
  }
  
  .login-footer a:hover {
    text-decoration: underline;
  }
  </style>