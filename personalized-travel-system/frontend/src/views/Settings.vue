<template>
  <div class="settings-container">
    <el-card class="settings-card">
      <template #header>
        <div class="settings-header">
          <h2>账户设置</h2>
        </div>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="个人信息" name="profile">
          <el-form :model="profileForm" :rules="profileRules" ref="profileFormRef" label-width="100px">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="profileForm.username" placeholder="请输入用户名"></el-input>
            </el-form-item>
            
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="profileForm.email" placeholder="请输入邮箱"></el-input>
            </el-form-item>
            
            <el-form-item label="手机号码" prop="phone">
              <el-input v-model="profileForm.phone" placeholder="请输入手机号码"></el-input>
            </el-form-item>
            
            <el-form-item label="所在地" prop="location">
              <el-input v-model="profileForm.location" placeholder="请输入所在地"></el-input>
            </el-form-item>
            
            <el-form-item label="个人简介">
              <el-input
                v-model="profileForm.bio"
                type="textarea"
                :rows="3"
                placeholder="请输入个人简介"
              ></el-input>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="updateProfile">保存信息</el-button>
              <el-button @click="resetProfileForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="修改密码" name="password">
          <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
            <el-form-item label="当前密码" prop="currentPassword">
              <el-input 
                v-model="passwordForm.currentPassword" 
                type="password" 
                placeholder="请输入当前密码"
                show-password
              ></el-input>
            </el-form-item>
            
            <el-form-item label="新密码" prop="newPassword">
              <el-input 
                v-model="passwordForm.newPassword" 
                type="password" 
                placeholder="请输入新密码"
                show-password
              ></el-input>
            </el-form-item>
            
            <el-form-item label="确认新密码" prop="confirmPassword">
              <el-input 
                v-model="passwordForm.confirmPassword" 
                type="password" 
                placeholder="请再次输入新密码"
                show-password
              ></el-input>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="updatePassword">修改密码</el-button>
              <el-button @click="resetPasswordForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="旅行偏好" name="preferences">
          <el-form :model="preferencesForm" ref="preferencesFormRef" label-width="100px">
            <el-form-item label="旅行类型">
              <el-checkbox-group v-model="preferencesForm.travelTypes">
                <el-checkbox label="文化体验">文化体验</el-checkbox>
                <el-checkbox label="自然风光">自然风光</el-checkbox>
                <el-checkbox label="美食探索">美食探索</el-checkbox>
                <el-checkbox label="历史古迹">历史古迹</el-checkbox>
                <el-checkbox label="休闲度假">休闲度假</el-checkbox>
                <el-checkbox label="冒险刺激">冒险刺激</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            
            <el-form-item label="预算范围">
              <el-select v-model="preferencesForm.budgetRange" placeholder="请选择预算范围">
                <el-option label="经济型" value="economy"></el-option>
                <el-option label="中等" value="moderate"></el-option>
                <el-option label="豪华" value="luxury"></el-option>
              </el-select>
            </el-form-item>
            
            <el-form-item label="食物偏好">
              <el-checkbox-group v-model="preferencesForm.foodPreferences">
                <el-checkbox label="当地特色">当地特色</el-checkbox>
                <el-checkbox label="素食">素食</el-checkbox>
                <el-checkbox label="海鲜">海鲜</el-checkbox>
                <el-checkbox label="辛辣">辛辣</el-checkbox>
                <el-checkbox label="甜点">甜点</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="updatePreferences">保存偏好</el-button>
              <el-button @click="resetPreferencesForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="通知设置" name="notifications">
          <el-form :model="notificationForm" ref="notificationFormRef" label-width="100px">
            <el-form-item label="邮件通知">
              <el-switch v-model="notificationForm.emailNotifications"></el-switch>
            </el-form-item>
            
            <el-form-item label="推荐更新">
              <el-switch v-model="notificationForm.recommendationUpdates"></el-switch>
            </el-form-item>
            
            <el-form-item label="系统消息">
              <el-switch v-model="notificationForm.systemMessages"></el-switch>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="updateNotifications">保存设置</el-button>
              <el-button @click="resetNotificationForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../store'

const router = useRouter()
const userStore = useUserStore()

// 检查用户是否登录
if (!userStore.isLoggedIn) {
  ElMessage.warning('请先登录')
  router.push('/login?redirect=/profile/settings')
}

// 当前激活的标签页
const activeTab = ref('profile')

// 表单引用
const profileFormRef = ref(null)
const passwordFormRef = ref(null)
const preferencesFormRef = ref(null)
const notificationFormRef = ref(null)

// 个人信息表单
const profileForm = reactive({
  username: '',
  email: '',
  phone: '',
  location: '',
  bio: ''
})

// 密码表单
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 旅行偏好表单
const preferencesForm = reactive({
  travelTypes: [],
  budgetRange: '',
  foodPreferences: []
})

// 通知设置表单
const notificationForm = reactive({
  emailNotifications: true,
  recommendationUpdates: true,
  systemMessages: true
})

// 个人信息表单验证规则
const profileRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ]
}

// 密码表单验证规则
const passwordRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6个字符', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 获取用户信息
const fetchUserData = () => {
  // 获取当前用户信息
  const userInfo = userStore.getUserInfo
  
  if (userInfo) {
    // 填充个人信息表单
    profileForm.username = userInfo.username || ''
    profileForm.email = userInfo.email || ''
    profileForm.phone = userInfo.phone || ''
    profileForm.location = userInfo.location || ''
    profileForm.bio = userInfo.bio || ''
    
    // 获取用户偏好设置
    const preferences = userStore.getUserPreferences
    if (preferences) {
      preferencesForm.travelTypes = preferences.travelTypes || []
      preferencesForm.budgetRange = preferences.budgetRange || ''
      preferencesForm.foodPreferences = preferences.foodPreferences || []
    }
    
    // 这里可以添加获取通知设置的逻辑
  }
}

// 更新个人信息
const updateProfile = async () => {
  if (!profileFormRef.value) return
  
  await profileFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // 模拟API请求
        // 实际项目中应该调用真实的API
        console.log('提交的个人信息:', profileForm)
        
        // 模拟成功响应
        setTimeout(() => {
          // 更新本地存储的用户信息
          const currentUserInfo = userStore.getUserInfo
          userStore.setUserInfo({
            ...currentUserInfo,
            username: profileForm.username,
            email: profileForm.email,
            phone: profileForm.phone,
            location: profileForm.location,
            bio: profileForm.bio
          })
          
          ElMessage.success('个人信息更新成功')
        }, 1000)
        
        // 实际API调用示例
        /*
        const response = await fetch('/api/user/profile', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${userStore.token}`
          },
          body: JSON.stringify(profileForm)
        })
        
        const data = await response.json()
        
        if (data.success) {
          // 更新本地存储的用户信息
          userStore.setUserInfo(data.user)
          ElMessage.success('个人信息更新成功')
        } else {
          ElMessage.error(data.message || '更新失败，请重试')
        }
        */
      } catch (error) {
        console.error('更新个人信息时出错:', error)
        ElMessage.error('更新失败，请重试')
      }
    } else {
      ElMessage.warning('请完善表单信息')
      return false
    }
  })
}

// 更新密码
const updatePassword = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // 模拟API请求
        // 实际项目中应该调用真实的API
        console.log('提交的密码信息:', passwordForm)
        
        // 模拟成功响应
        setTimeout(() => {
          ElMessage.success('密码修改成功，请重新登录')
          // 退出登录，重定向到登录页
          userStore.logout()
          router.push('/login')
        }, 1000)
        
        // 实际API调用示例
        /*
        const response = await fetch('/api/user/password', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${userStore.token}`
          },
          body: JSON.stringify({
            currentPassword: passwordForm.currentPassword,
            newPassword: passwordForm.newPassword
          })
        })
        
        const data = await response.json()
        
        if (data.success) {
          ElMessage.success('密码修改成功，请重新登录')
          // 退出登录，重定向到登录页
          userStore.logout()
          router.push('/login')
        } else {
          ElMessage.error(data.message || '修改失败，请检查当前密码是否正确')
        }
        */
      } catch (error) {
        console.error('修改密码时出错:', error)
        ElMessage.error('修改失败，请重试')
      }
    } else {
      ElMessage.warning('请完善表单信息')
      return false
    }
  })
}

// 更新旅行偏好
const updatePreferences = async () => {
  try {
    // 模拟API请求
    // 实际项目中应该调用真实的API
    console.log('提交的偏好设置:', preferencesForm)
    
    // 模拟成功响应
    setTimeout(() => {
      // 更新本地存储的偏好设置
      userStore.setPreferences({
        travelTypes: preferencesForm.travelTypes,
        budgetRange: preferencesForm.budgetRange,
        foodPreferences: preferencesForm.foodPreferences
      })
      
      ElMessage.success('旅行偏好更新成功')
    }, 1000)
    
    // 实际API调用示例
    /*
    const response = await fetch('/api/user/preferences', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userStore.token}`
      },
      body: JSON.stringify(preferencesForm)
    })
    
    const data = await response.json()
    
    if (data.success) {
      // 更新本地存储的偏好设置
      userStore.setPreferences(data.preferences)
      ElMessage.success('旅行偏好更新成功')
    } else {
      ElMessage.error(data.message || '更新失败，请重试')
    }
    */
  } catch (error) {
    console.error('更新旅行偏好时出错:', error)
    ElMessage.error('更新失败，请重试')
  }
}

// 更新通知设置
const updateNotifications = async () => {
  try {
    // 模拟API请求
    // 实际项目中应该调用真实的API
    console.log('提交的通知设置:', notificationForm)
    
    // 模拟成功响应
    setTimeout(() => {
      ElMessage.success('通知设置更新成功')
    }, 1000)
    
    // 实际API调用示例
    /*
    const response = await fetch('/api/user/notifications', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userStore.token}`
      },
      body: JSON.stringify(notificationForm)
    })
    
    const data = await response.json()
    
    if (data.success) {
      ElMessage.success('通知设置更新成功')
    } else {
      ElMessage.error(data.message || '更新失败，请重试')
    }
    */
  } catch (error) {
    console.error('更新通知设置时出错:', error)
    ElMessage.error('更新失败，请重试')
  }
}

// 重置表单
const resetProfileForm = () => {
  if (profileFormRef.value) {
    profileFormRef.value.resetFields()
    fetchUserData() // 重新获取用户数据
  }
}

const resetPasswordForm = () => {
  if (passwordFormRef.value) {
    passwordFormRef.value.resetFields()
  }
}

const resetPreferencesForm = () => {
  if (preferencesFormRef.value) {
    preferencesFormRef.value.resetFields()
    fetchUserData() // 重新获取用户数据
  }
}

const resetNotificationForm = () => {
  if (notificationFormRef.value) {
    notificationFormRef.value.resetFields()
  }
}

// 组件挂载时获取用户数据
onMounted(() => {
  fetchUserData()
})
</script>

<style scoped lang="scss">
.settings-container {
  max-width: 800px;
  margin: 20px auto;
  padding: 0 20px;
}

.settings-card {
  margin-bottom: 30px;
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>