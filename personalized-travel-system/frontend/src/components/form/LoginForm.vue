<template>
  <div class="login-form">
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-position="top"
      @submit.prevent="handleSubmit"
    >
      <el-form-item label="用户名/邮箱" prop="username">
        <el-input 
          v-model="formData.username" 
          placeholder="请输入用户名或邮箱"
          prefix-icon="el-icon-user"
        />
      </el-form-item>
      
      <el-form-item label="密码" prop="password">
        <el-input 
          v-model="formData.password" 
          type="password" 
          placeholder="请输入密码"
          prefix-icon="el-icon-lock"
          show-password
        />
      </el-form-item>
      
      <div class="form-options">
        <el-checkbox v-model="formData.remember">记住我</el-checkbox>
        <el-button type="text" @click="$emit('forgotPassword')">忘记密码?</el-button>
      </div>
      
      <el-form-item>
        <el-button 
          type="primary" 
          native-type="submit" 
          :loading="loading" 
          class="submit-button"
        >
          登录
        </el-button>
      </el-form-item>
      
      <div class="form-footer">
        <span>还没有账号?</span>
        <el-button type="text" @click="$emit('switchToRegister')">立即注册</el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../store'

// 定义组件属性
const props = defineProps({
  redirectUrl: {
    type: String,
    default: '/'
  }
})

// 定义组件事件
const emit = defineEmits(['success', 'error', 'forgotPassword', 'switchToRegister'])

// 路由和状态管理
const router = useRouter()
const userStore = useUserStore()

// 表单引用
const formRef = ref(null)

// 加载状态
const loading = ref(false)

// 表单数据
const formData = reactive({
  username: '',
  password: '',
  remember: false
})

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名或邮箱', trigger: 'blur' },
    { min: 3, message: '用户名长度不能小于3个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6个字符', trigger: 'blur' }
  ]
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid, fields) => {
    if (valid) {
      try {
        loading.value = true
        
        // 这里应该调用实际的登录API
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // 模拟成功响应
        const response = {
          token: 'mock-token-12345',
          user: {
            id: 1,
            username: formData.username,
            email: `${formData.username}@example.com`,
            avatar: null
          }
        }
        
        // 存储用户信息和token
        userStore.setToken(response.token)
        userStore.setUserInfo(response.user)
        
        ElMessage.success('登录成功')
        emit('success', response)
        
        // 重定向到指定页面或首页
        router.push(props.redirectUrl)
      } catch (error) {
        console.error('登录失败:', error)
        ElMessage.error('登录失败，请检查用户名和密码')
        emit('error', error)
      } finally {
        loading.value = false
      }
    } else {
      console.log('表单验证失败:', fields)
    }
  })
}
</script>

<style scoped>
.login-form {
  width: 100%;
  max-width: 400px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.submit-button {
  width: 100%;
  padding: 12px 0;
  font-size: 16px;
}

.form-footer {
  margin-top: 20px;
  text-align: center;
}
</style>