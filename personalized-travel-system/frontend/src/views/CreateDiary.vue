<template>
  <div class="create-diary-container">
    <el-card class="diary-card">
      <template #header>
        <div class="diary-header">
          <h2>创建旅游日记</h2>
        </div>
      </template>
      
      <el-form :model="diaryForm" :rules="rules" ref="diaryFormRef" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="diaryForm.title" placeholder="请输入日记标题"></el-input>
        </el-form-item>
        
        <el-form-item label="地点" prop="location">
          <el-input v-model="diaryForm.location" placeholder="请输入旅行地点"></el-input>
        </el-form-item>
        
        <el-form-item label="日期" prop="date">
          <el-date-picker
            v-model="diaryForm.date"
            type="date"
            placeholder="选择旅行日期"
            style="width: 100%"
          ></el-date-picker>
        </el-form-item>
        
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="diaryForm.content"
            type="textarea"
            :rows="6"
            placeholder="分享您的旅行体验..."
          ></el-input>
        </el-form-item>
        
        <el-form-item label="标签">
          <el-select
            v-model="diaryForm.tags"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="请选择或创建标签"
            style="width: 100%"
          >
            <el-option
              v-for="tag in tagOptions"
              :key="tag"
              :label="tag"
              :value="tag"
            ></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="图片">
          <el-upload
            action="/api/upload"
            list-type="picture-card"
            :on-preview="handlePictureCardPreview"
            :on-remove="handleRemove"
            :on-success="handleUploadSuccess"
          >
            <i class="el-icon-plus"></i>
          </el-upload>
          <el-dialog v-model="dialogVisible">
            <img width="100%" :src="dialogImageUrl" alt="预览图片">
          </el-dialog>
        </el-form-item>
        
        <el-form-item label="评分" prop="rating">
          <el-rate
            v-model="diaryForm.rating"
            :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
            :texts="['失望', '一般', '满意', '推荐', '极力推荐']"
            show-text
          ></el-rate>
        </el-form-item>
        
        <el-form-item label="公开" prop="isPublic">
          <el-switch v-model="diaryForm.isPublic"></el-switch>
          <span class="privacy-hint">{{ diaryForm.isPublic ? '所有人可见' : '仅自己可见' }}</span>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="submitForm">发布日记</el-button>
          <el-button @click="resetForm">重置</el-button>
          <el-button @click="$router.push('/diary')">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../store'

const router = useRouter()
const userStore = useUserStore()

// 表单引用
const diaryFormRef = ref(null)

// 表单数据
const diaryForm = reactive({
  title: '',
  location: '',
  date: new Date(),
  content: '',
  tags: [],
  images: [],
  rating: 3,
  isPublic: true
})

// 表单验证规则
const rules = {
  title: [
    { required: true, message: '请输入日记标题', trigger: 'blur' },
    { min: 2, max: 50, message: '标题长度应在2到50个字符之间', trigger: 'blur' }
  ],
  location: [
    { required: true, message: '请输入旅行地点', trigger: 'blur' }
  ],
  date: [
    { required: true, message: '请选择旅行日期', trigger: 'change' }
  ],
  content: [
    { required: true, message: '请输入日记内容', trigger: 'blur' },
    { min: 10, message: '内容不能少于10个字符', trigger: 'blur' }
  ],
  rating: [
    { required: true, message: '请给您的旅行体验评分', trigger: 'change' }
  ]
}

// 标签选项
const tagOptions = [
  '美食', '风景', '文化', '历史', '购物', '冒险', '放松', '自然', '城市', '海滩'
]

// 图片上传相关
const dialogImageUrl = ref('')
const dialogVisible = ref(false)

const handleRemove = (file, fileList) => {
  diaryForm.images = diaryForm.images.filter(img => img.url !== file.url)
}

const handlePictureCardPreview = (file) => {
  dialogImageUrl.value = file.url
  dialogVisible.value = true
}

const handleUploadSuccess = (response, file, fileList) => {
  if (response.success) {
    diaryForm.images.push({
      url: response.url,
      name: file.name
    })
    ElMessage.success('图片上传成功')
  } else {
    ElMessage.error('图片上传失败')
  }
}

// 提交表单
const submitForm = async () => {
  if (!diaryFormRef.value) return
  
  await diaryFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // 模拟API请求
        // 实际项目中应该调用真实的API
        console.log('提交的日记数据:', diaryForm)
        
        // 模拟成功响应
        setTimeout(() => {
          ElMessage.success('日记发布成功')
          router.push('/diary')
        }, 1000)
        
        // 实际API调用示例
        /*
        const response = await fetch('/api/diaries', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${userStore.token}`
          },
          body: JSON.stringify(diaryForm)
        })
        
        const data = await response.json()
        
        if (data.success) {
          ElMessage.success('日记发布成功')
          router.push('/diary')
        } else {
          ElMessage.error(data.message || '发布失败，请重试')
        }
        */
      } catch (error) {
        console.error('发布日记时出错:', error)
        ElMessage.error('发布失败，请重试')
      }
    } else {
      ElMessage.warning('请完善表单信息')
      return false
    }
  })
}

// 重置表单
const resetForm = () => {
  if (diaryFormRef.value) {
    diaryFormRef.value.resetFields()
    diaryForm.images = []
  }
}

// 检查用户是否登录
if (!userStore.isLoggedIn) {
  ElMessage.warning('请先登录')
  router.push('/login?redirect=/diary/create')
}
</script>

<style scoped lang="scss">
.create-diary-container {
  max-width: 800px;
  margin: 20px auto;
  padding: 0 20px;
}

.diary-card {
  margin-bottom: 30px;
}

.diary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.privacy-hint {
  margin-left: 10px;
  font-size: 12px;
  color: #909399;
}
</style>