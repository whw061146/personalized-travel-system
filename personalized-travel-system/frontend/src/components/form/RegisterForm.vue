<template>
  <div class="register-form">
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-position="top"
      @submit.prevent="handleSubmit"
    >
      <el-form-item label="用户名" prop="username">
        <el-input 
          v-model="formData.username" 
          placeholder="请输入用户名"
          prefix-icon="el-icon-user"
        />
      </el-form-item>
      
      <el-form-item label="邮箱" prop="email">
        <el-input 
          v-model="formData.email" 
          placeholder="请输入邮箱"
          prefix-icon="el-icon-message"
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
      
      <el-form-item label="确认密码" prop="confirmPassword">
        <el-input 
          v-model="formData.confirmPassword" 
          type="password" 
          placeholder="请再次输入密码"
          prefix-icon="el-icon-lock"
          show-password
        />
      </el-form-item>
      
      <el-form-item>
        <el-checkbox v-model="formData.agreement" label="我已阅读并同意" />
        <el-button type="text" @click="showTerms = true">用户协议和隐私政策</el-button>
      </el-form-item>
      
      <el-form-item>
        <el-button 
          type="primary" 
          native-type="submit" 
          :loading="loading" 
          class="submit-button"
          :disabled="!formData.agreement"
        >
          注册
        </el-button>
      </el-form-item>
      
      <div class="form-footer">
        <span>已有账号?</span>
        <el-button type="text" @click="$emit('switchToLogin')">立即登录</el-button>
      </div>
    </el-form>
    
    <!-- 用户协议对话框 -->
    <el-dialog
      v-model="showTerms"
      title="用户协议和隐私政策"
      width="70%"
    >
      <div class="terms-content">
        <h3>用户协议</h3>
        <p>欢迎使用个性化旅游推荐系统。请仔细阅读以下条款，使用本服务即表示您同意接受这些条款。</p>
        <p>本协议包含了您使用我们服务的权利和限制，以及您与我们之间的法律关系。</p>
        
        <h3>隐私政策</h3>
        <p>我们重视您的隐私。我们收集的信息将用于改善服务质量和用户体验。</p>
        <p>我们不会未经您的许可向第三方出售或出租您的个人信息。</p>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showTerms = false">关闭</el-button>
          <el-button type="primary" @click="acceptTerms">同意</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../store'

// 定义组件事件
const emit = defineEmits(['success', 'error', 'switchToLogin'])

// 路由和状态管理
const router = useRouter()
const userStore = useUserStore()

// 表单引用
const formRef = ref(null)

// 加载状态
const loading = ref(false)

// 用户协议对话框
const showTerms = ref(false)

// 表单数据
const formData = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreement: false
})

// 验证密码是否一致
const validatePass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== formData.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validatePass, trigger: ['blur', 'change'] }
  ]
}

// 同意用户协议
const acceptTerms = () => {
  formData.agreement = true
  showTerms.value = false
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid, fields) => {
    if (valid) {
      if (!formData.agreement) {
        ElMessage.warning('请阅读并同意用户协议和隐私政策')
        return
      }
      
      try {
        loading.value = true
        
        // 这里应该调用实际的注册API
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 1500))
        
        // 模拟成功响应
        const response = {
          token: 'mock-token-register-12345',
          user: {
            id: 2,
            username: formData.username,
            email: formData.email,
            avatar: null
          }
        }
        
        // 存储用户信息和token
        userStore.setToken(response.token)
        userStore.setUserInfo(response.user)
        
        ElMessage.success('注册成功')
        emit('success', response)
        
        // 注册成功后跳转到首页
        router.push('/')
      } catch (error) {
        console.error('注册失败:', error)
        ElMessage.error('注册失败，请稍后再试')
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
.register-form {
  width: 100%;
  max-width: 400px;
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

.terms-content {
  max-height: 300px;
  overflow-y: auto;
  padding: 0 10px;
}

.terms-content h3 {
  margin-top: 20px;
  margin-bottom: 10px;
}

.terms-content p {
  margin-bottom: 15px;
  line-height: 1.5;
}
</style>