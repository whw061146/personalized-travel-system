<template>
  <div class="preferences-form">
    <el-form
      ref="formRef"
      :model="formData"
      label-position="top"
      @submit.prevent="handleSubmit"
    >
      <h3>旅行偏好设置</h3>
      <p class="form-description">设置您的旅行偏好，我们将为您提供更加个性化的推荐</p>
      
      <el-form-item label="旅行类型">
        <el-select
          v-model="formData.travelTypes"
          multiple
          placeholder="选择您喜欢的旅行类型"
          style="width: 100%"
        >
          <el-option
            v-for="item in travelTypeOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-form-item>
      
      <el-form-item label="美食偏好">
        <el-select
          v-model="formData.foodPreferences"
          multiple
          collapse-tags
          placeholder="选择您喜欢的美食类型"
          style="width: 100%"
        >
          <el-option
            v-for="item in foodOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-form-item>
      
      <el-form-item label="预算范围">
        <el-slider
          v-model="formData.budgetRange"
          range
          :min="0"
          :max="10000"
          :step="100"
          :marks="budgetMarks"
        />
      </el-form-item>
      
      <el-form-item label="住宿偏好">
        <el-radio-group v-model="formData.accommodation">
          <el-radio label="budget">经济型</el-radio>
          <el-radio label="mid">中档</el-radio>
          <el-radio label="luxury">豪华</el-radio>
        </el-radio-group>
      </el-form-item>
      
      <el-form-item label="旅行时长 (天)">
        <el-input-number 
          v-model="formData.tripDuration" 
          :min="1" 
          :max="30" 
          :step="1"
          style="width: 180px"
        />
      </el-form-item>
      
      <el-form-item>
        <el-button 
          type="primary" 
          native-type="submit" 
          :loading="loading" 
          class="submit-button"
        >
          保存偏好
        </el-button>
        <el-button @click="resetForm">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../../store'

// 定义组件属性
const props = defineProps({
  initialPreferences: {
    type: Object,
    default: () => ({})
  }
})

// 定义组件事件
const emit = defineEmits(['success', 'cancel'])

// 状态管理
const userStore = useUserStore()

// 表单引用
const formRef = ref(null)

// 加载状态
const loading = ref(false)

// 旅行类型选项
const travelTypeOptions = [
  { value: 'cultural', label: '文化体验' },
  { value: 'nature', label: '自然风光' },
  { value: 'adventure', label: '探险' },
  { value: 'relaxation', label: '休闲放松' },
  { value: 'urban', label: '城市观光' },
  { value: 'rural', label: '乡村体验' },
  { value: 'historical', label: '历史古迹' },
  { value: 'shopping', label: '购物' }
]

// 美食选项
const foodOptions = [
  { value: 'local', label: '当地特色' },
  { value: 'chinese', label: '中餐' },
  { value: 'western', label: '西餐' },
  { value: 'japanese', label: '日料' },
  { value: 'korean', label: '韩餐' },
  { value: 'seafood', label: '海鲜' },
  { value: 'vegetarian', label: '素食' },
  { value: 'spicy', label: '麻辣' },
  { value: 'sweet', label: '甜点' },
  { value: 'street', label: '街边小吃' }
]

// 预算标记
const budgetMarks = {
  0: '¥0',
  2000: '¥2000',
  5000: '¥5000',
  10000: '¥10000+'
}

// 表单数据
const formData = reactive({
  travelTypes: [],
  foodPreferences: [],
  budgetRange: [1000, 3000],
  accommodation: 'mid',
  tripDuration: 3
})

// 初始化表单数据
onMounted(() => {
  // 如果有初始偏好设置，则加载
  if (props.initialPreferences) {
    const { travelTypes, foodPreferences, budgetRange, accommodation, tripDuration } = props.initialPreferences
    
    if (travelTypes) formData.travelTypes = travelTypes
    if (foodPreferences) formData.foodPreferences = foodPreferences
    if (budgetRange) formData.budgetRange = budgetRange
    if (accommodation) formData.accommodation = accommodation
    if (tripDuration) formData.tripDuration = tripDuration
  } else {
    // 尝试从用户存储中获取偏好
    const userPreferences = userStore.getUserPreferences
    if (userPreferences) {
      const { travelTypes, foodPreferences, budgetRange } = userPreferences
      
      if (travelTypes) formData.travelTypes = travelTypes
      if (foodPreferences) formData.foodPreferences = foodPreferences
      if (budgetRange) formData.budgetRange = budgetRange
    }
  }
})

// 重置表单
const resetForm = () => {
  formData.travelTypes = []
  formData.foodPreferences = []
  formData.budgetRange = [1000, 3000]
  formData.accommodation = 'mid'
  formData.tripDuration = 3
}

// 提交表单
const handleSubmit = async () => {
  try {
    loading.value = true
    
    // 准备要保存的偏好数据
    const preferences = {
      travelTypes: formData.travelTypes,
      foodPreferences: formData.foodPreferences,
      budgetRange: formData.budgetRange,
      accommodation: formData.accommodation,
      tripDuration: formData.tripDuration
    }
    
    // 保存到用户状态
    userStore.setPreferences(preferences)
    
    // 这里可以添加实际的API调用来保存到后端
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 800))
    
    ElMessage.success('偏好设置已保存')
    emit('success', preferences)
  } catch (error) {
    console.error('保存偏好失败:', error)
    ElMessage.error('保存失败，请稍后再试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.preferences-form {
  width: 100%;
  max-width: 600px;
}

.form-description {
  color: #606266;
  margin-bottom: 20px;
}

.submit-button {
  min-width: 120px;
}
</style>