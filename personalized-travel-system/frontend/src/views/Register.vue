<template>
    <div class="register-container">
      <div class="register-card">
        <div class="register-header">
          <h2>注册账号</h2>
          <p>创建您的个人账号，开启专属旅行体验</p>
        </div>
        
        <el-form
          ref="registerFormRef"
          :model="registerForm"
          :rules="registerRules"
          label-position="top"
          @submit.prevent="handleRegister"
        >
          <el-form-item label="用户名" prop="username">
            <el-input 
              v-model="registerForm.username" 
              placeholder="请输入用户名"
              prefix-icon="el-icon-user"
            />
          </el-form-item>
          
          <el-form-item label="邮箱" prop="email">
            <el-input 
              v-model="registerForm.email" 
              placeholder="请输入邮箱"
              prefix-icon="el-icon-message"
            />
          </el-form-item>
          
          <el-form-item label="密码" prop="password">
            <el-input 
              v-model="registerForm.password" 
              type="password" 
              placeholder="请输入密码"
              prefix-icon="el-icon-lock"
              show-password
            />
          </el-form-item>
          
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input 
              v-model="registerForm.confirmPassword" 
              type="password" 
              placeholder="请再次输入密码"
              prefix-icon="el-icon-lock"
              show-password
            />
          </el-form-item>
          
          <el-form-item>
            <el-checkbox v-model="agreeTerms" @change="validateAgreeTerms">我已阅读并同意<el-button type="text" @click="showTerms">服务条款</el-button></el-checkbox>
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              native-type="submit" 
              :loading="loading" 
              :disabled="!agreeTerms"
              class="register-button"
            >
              注册
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="register-footer">
          <p>已有账号? <router-link to="/login">立即登录</router-link></p>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive } from 'vue'
  import { useRouter } from 'vue-router'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import { useUserStore } from '../store'
  
  // 路由实例
  const router = useRouter()
  
  // 用户状态管理
  const userStore = useUserStore()
  
  // 表单引用
  const registerFormRef = ref(null)
  
  // 加载状态
  const loading = ref(false)
  
  // 同意条款
  const agreeTerms = ref(false)
  
  // 注册表单数据
  const registerForm = reactive({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  })
  
  // 验证密码是否一致
  const validatePass = (rule, value, callback) => {
    if (value === '') {
      callback(new Error('请再次输入密码'))
    } else if (value !== registerForm.password) {
      callback(new Error('两次输入密码不一致'))
    } else {
      callback()
    }
  }
  
  // 验证是否同意条款
  const validateAgreeTerms = () => {
    if (!agreeTerms.value) {
      ElMessage.warning('请阅读并同意服务条款')
    }
  }
  
  // 表单验证规则
  const registerRules = {
    username: [
      { required: true, message: '请输入用户名', trigger: 'blur' },
      { min: 3, max: 20, message: '长度在3到20个字符之间', trigger: 'blur' }
    ],
    email: [
      { required: true, message: '请输入邮箱地址', trigger: 'blur' },
      { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
    ],
    password: [
      { required: true, message: '请输入密码', trigger: 'blur' },
      { min: 6, max: 20, message: '长度在6到20个字符之间', trigger: 'blur' }
    ],
    confirmPassword: [
      { required: true, message: '请再次输入密码', trigger: 'blur' },
      { validator: validatePass, trigger: 'blur' }
    ]
  }
  
  // 显示服务条款
  const showTerms = () => {
    ElMessageBox.alert(
      '欢迎使用个性化旅游推荐系统！使用本服务前，请您仔细阅读以下条款：\n\n' +
      '1. 本系统仅提供旅游信息推荐服务，不承担任何旅行安排责任\n' +
      '2. 用户需对账号安全负责，请妥善保管密码\n' +
      '3. 用户上传的内容需遵守相关法律法规\n' +
      '4. 我们会收集必要的用户数据以提供个性化服务\n' +
      '5. 用户可随时删除账号及相关数据',
      '服务条款',
      {
        confirmButtonText: '我已阅读并同意',
        callback: (action) => {
          if (action === 'confirm') {
            agreeTerms.value = true
          }
        }
      }
    )
  }
  
  // 注册处理函数
  const handleRegister = async () => {
    if (!registerFormRef.value) return
    
    await registerFormRef.value.validate(async (valid) => {
      if (valid) {
        if (!agreeTerms.value) {
          ElMessage.warning('请阅读并同意服务条款')
          return
        }
        
        try {
          loading.value = true
          
          // 调用注册API
          const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              username: registerForm.username,
              email: registerForm.email,
              password: registerForm.password
            })
          })
          
          const data = await response.json()
          
          if (response.ok) {
            // 注册成功
            ElMessage.success('注册成功，请登录')
            router.push('/login')
          } else {
            ElMessage.error(data.message || '注册失败，请稍后再试')
          }
        } catch (error) {
          console.error('注册错误:', error)
          ElMessage.error('注册过程中发生错误，请稍后再试')
        } finally {
          loading.value = false
        }
      }
    })
  }
  </script>
  
  <style scoped>
  .register-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: calc(100vh - 120px); /* 减去header和footer的高度 */
    background-color: #f5f7fa;
    padding: 20px;
  }
  
  .register-card {
    width: 100%;
    max-width: 400px;
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    padding: 30px;
  }
  
  .register-header {
    text-align: center;
    margin-bottom: 30px;
  }
  
  .register-header h2 {
    font-size: 24px;
    color: #303133;
    margin-bottom: 10px;
  }
  
  .register-header p {
    color: #909399;
    font-size: 14px;
  }
  
  .register-button {
    width: 100%;
    padding: 12px 0;
    font-size: 16px;
  }
  
  .register-footer {
    text-align: center;
    margin-top: 20px;
    color: #606266;
  }
  
  .register-footer a {
    color: #409EFF;
    text-decoration: none;
  }
  
  .register-footer a:hover {
    text-decoration: underline;
  }
  </style>