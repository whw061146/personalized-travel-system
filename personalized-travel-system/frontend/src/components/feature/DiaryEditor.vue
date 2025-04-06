<template>
  <div class="diary-editor">
    <el-form :model="diaryForm" :rules="rules" ref="diaryFormRef">
      <el-form-item label="标题" prop="title">
        <el-input v-model="diaryForm.title" placeholder="请输入旅行日记标题"></el-input>
      </el-form-item>
      
      <el-form-item label="旅行地点" prop="location">
        <el-input v-model="diaryForm.location" placeholder="请输入旅行地点"></el-input>
      </el-form-item>
      
      <el-form-item label="旅行日期" prop="travelDate">
        <el-date-picker
          v-model="diaryForm.travelDate"
          type="date"
          placeholder="选择日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
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
        >
          <el-option
            v-for="tag in availableTags"
            :key="tag"
            :label="tag"
            :value="tag"
          ></el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="图片上传">
        <el-upload
          action="#"
          list-type="picture-card"
          :auto-upload="false"
          :on-change="handleImageChange"
          :on-remove="handleImageRemove"
          :file-list="diaryForm.images"
        >
          <i class="el-icon-plus"></i>
        </el-upload>
      </el-form-item>
      
      <el-form-item label="评分" prop="rating">
        <el-rate
          v-model="diaryForm.rating"
          :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
          :texts="['失望', '一般', '满意', '推荐', '极力推荐']"
          show-text
        ></el-rate>
      </el-form-item>
      
      <el-form-item label="是否公开" prop="isPublic">
        <el-switch
          v-model="diaryForm.isPublic"
          active-text="公开"
          inactive-text="私密"
        ></el-switch>
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="submitForm">保存日记</el-button>
        <el-button @click="resetForm">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

// 组件属性
const props = defineProps({
  initialData: {
    type: Object,
    default: () => ({})
  }
})

// 组件事件
const emit = defineEmits(['save', 'cancel'])

// 表单引用
const diaryFormRef = ref(null)

// 可用标签
const availableTags = [
  '自然风光', '人文历史', '美食探索', '城市观光', 
  '乡村体验', '海滩度假', '徒步旅行', '购物天堂'
]

// 表单数据
const diaryForm = reactive({
  title: props.initialData.title || '',
  location: props.initialData.location || '',
  travelDate: props.initialData.travelDate || '',
  content: props.initialData.content || '',
  tags: props.initialData.tags || [],
  images: props.initialData.images || [],
  rating: props.initialData.rating || 3,
  isPublic: props.initialData.isPublic !== undefined ? props.initialData.isPublic : true
})

// 表单验证规则
const rules = {
  title: [
    { required: true, message: '请输入日记标题', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  location: [
    { required: true, message: '请输入旅行地点', trigger: 'blur' }
  ],
  travelDate: [
    { required: true, message: '请选择旅行日期', trigger: 'change' }
  ],
  content: [
    { required: true, message: '请输入日记内容', trigger: 'blur' },
    { min: 10, message: '内容不能少于10个字符', trigger: 'blur' }
  ],
  rating: [
    { required: true, message: '请评分', trigger: 'change' }
  ]
}

// 处理图片变化
const handleImageChange = (file, fileList) => {
  diaryForm.images = fileList
}

// 处理图片移除
const handleImageRemove = (file, fileList) => {
  diaryForm.images = fileList
}

// 提交表单
const submitForm = async () => {
  if (!diaryFormRef.value) return
  
  await diaryFormRef.value.validate((valid, fields) => {
    if (valid) {
      // 处理图片上传
      const formData = {
        ...diaryForm,
        images: diaryForm.images.map(img => {
          // 如果是新上传的图片，需要处理文件对象
          if (img.raw) {
            return {
              name: img.name,
              url: URL.createObjectURL(img.raw),
              file: img.raw
            }
          }
          return img
        })
      }
      
      // 触发保存事件
      emit('save', formData)
      ElMessage.success('日记保存成功')
    } else {
      console.error('表单验证失败:', fields)
      ElMessage.error('请完善表单信息')
    }
  })
}

// 重置表单
const resetForm = () => {
  diaryFormRef.value?.resetFields()
}
</script>

<style scoped>
.diary-editor {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.el-form-item {
  margin-bottom: 22px;
}

.el-textarea__inner {
  font-family: inherit;
}

.el-upload--picture-card {
  width: 120px;
  height: 120px;
  line-height: 120px;
}
</style>