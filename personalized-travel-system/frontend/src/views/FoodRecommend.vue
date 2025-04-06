<template>
    <div class="food-recommend-container">
      <!-- 页面头部 -->
      <div class="food-header">
        <div class="container">
          <h1>美食推荐</h1>
          <p>发现当地特色美食，满足您的味蕾体验</p>
        </div>
      </div>
      
      <!-- 搜索和筛选区域 -->
      <div class="container search-filter-container">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="24" :md="16">
            <el-input
              v-model="searchQuery"
              placeholder="搜索美食或餐厅"
              prefix-icon="el-icon-search"
              clearable
              @keyup.enter="handleSearch"
            >
              <template #append>
                <el-button @click="handleSearch">搜索</el-button>
              </template>
            </el-input>
          </el-col>
          <el-col :xs="24" :sm="24" :md="8">
            <el-button @click="showFilterDrawer = true" icon="el-icon-filter">筛选</el-button>
            <el-button @click="resetFilters" icon="el-icon-refresh">重置</el-button>
          </el-col>
        </el-row>
      </div>
      
      <!-- 筛选抽屉 -->
      <el-drawer
        v-model="showFilterDrawer"
        title="筛选条件"
        direction="right"
        size="300px"
      >
        <div class="filter-drawer-content">
          <h3>美食类型</h3>
          <el-checkbox-group v-model="filters.foodTypes">
            <el-checkbox v-for="type in foodTypeOptions" :key="type.value" :label="type.value">{{ type.label }}</el-checkbox>
          </el-checkbox-group>
          
          <h3>价格区间</h3>
          <el-slider
            v-model="filters.priceRange"
            range
            :min="0"
            :max="500"
            :step="10"
          >
            <template #default="{ modelValue }">
              <div>¥{{ modelValue[0] }} - ¥{{ modelValue[1] }}</div>
            </template>
          </el-slider>
          
          <h3>评分</h3>
          <el-rate v-model="filters.minRating" :texts="ratingTexts" show-text />
          
          <h3>距离</h3>
          <el-radio-group v-model="filters.distance">
            <el-radio :label="1">1公里内</el-radio>
            <el-radio :label="3">3公里内</el-radio>
            <el-radio :label="5">5公里内</el-radio>
            <el-radio :label="10">10公里内</el-radio>
            <el-radio :label="0">不限</el-radio>
          </el-radio-group>
          
          <div class="filter-actions">
            <el-button type="primary" @click="applyFilters">应用筛选</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </div>
        </div>
      </el-drawer>
      
      <!-- 美食内容区域 -->
      <div class="container food-content">
        <!-- 活跃筛选条件 -->
        <div class="active-filters" v-if="hasActiveFilters">
          <span class="filter-label">已选筛选条件:</span>
          <el-tag 
            v-for="type in filters.foodTypes" 
            :key="`type-${type}`" 
            closable 
            @close="removeFilter('foodType', type)"
          >
            {{ getFoodTypeLabel(type) }}
          </el-tag>
          <el-tag 
            v-if="filters.priceRange[0] > 0 || filters.priceRange[1] < 500" 
            closable 
            @close="removeFilter('priceRange')"
          >
            价格: ¥{{ filters.priceRange[0] }} - ¥{{ filters.priceRange[1] }}
          </el-tag>
          <el-tag 
            v-if="filters.minRating > 0" 
            closable 
            @close="removeFilter('minRating')"
          >
            评分: {{ filters.minRating }}星以上
          </el-tag>
          <el-tag 
            v-if="filters.distance > 0" 
            closable 
            @close="removeFilter('distance')"
          >
            距离: {{ filters.distance }}公里内
          </el-tag>
        </div>
        
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="5" animated />
        </div>
        
        <!-- 无结果提示 -->
        <el-empty v-else-if="foods.length === 0" description="暂无符合条件的美食">
          <el-button @click="resetFilters">重置筛选条件</el-button>
        </el-empty>
        
        <!-- 美食列表 -->
        <el-row v-else :gutter="20">
          <el-col v-for="food in foods" :key="food.id" :xs="24" :sm="12" :md="8" :lg="6">
            <el-card class="food-card" shadow="hover" @click="viewFoodDetail(food.id)">
              <div class="food-image">
                <el-image :src="food.image || '@/assets/default-food.jpg'" fit="cover" />
                <div class="food-price" v-if="food.price">
                  <span>¥{{ food.price }}</span>
                </div>
              </div>
              <div class="food-info">
                <h3 class="food-name">{{ food.name }}</h3>
                <div class="food-meta">
                  <el-rate v-model="food.rating" disabled text-color="#ff9900" />
                  <span class="food-rating-value">{{ food.rating.toFixed(1) }}</span>
                </div>
                <p class="food-description">{{ food.description }}</p>
                <div class="food-tags">
                  <el-tag size="small" v-for="tag in food.tags" :key="tag">{{ tag }}</el-tag>
                </div>
                <div class="restaurant-info">
                  <i class="el-icon-location"></i>
                  <span>{{ food.restaurant.name }}</span>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
        
        <!-- 分页 -->
        <div class="pagination-container" v-if="totalItems > 0">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[12, 24, 36, 48]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="totalItems"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive, computed, onMounted, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import { useUserStore, useRecommendStore, useSettingsStore } from '../store'
  
  // 路由实例
  const router = useRouter()
  
  // 状态管理
  const userStore = useUserStore()
  const recommendStore = useRecommendStore()
  const settingsStore = useSettingsStore()
  
  // 页面状态
  const loading = ref(false)
  const foods = ref([])
  const totalItems = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(12)
  const searchQuery = ref('')
  const showFilterDrawer = ref(false)
  
  // 筛选条件
  const filters = reactive({
    foodTypes: [],
    priceRange: [0, 500],
    minRating: 0,
    distance: 0
  })
  
  // 美食类型选项
  const foodTypeOptions = [
    { label: '中餐', value: 'chinese' },
    { label: '西餐', value: 'western' },
    { label: '日料', value: 'japanese' },
    { label: '韩餐', value: 'korean' },
    { label: '东南亚', value: 'southeast_asian' },
    { label: '快餐', value: 'fast_food' },
    { label: '火锅', value: 'hotpot' },
    { label: '烧烤', value: 'bbq' },
    { label: '甜点', value: 'dessert' },
    { label: '饮品', value: 'drinks' }
  ]
  
  // 评分文本
  const ratingTexts = ['极差', '失望', '一般', '满意', '很棒']
  
  // 计算是否有活跃的筛选条件
  const hasActiveFilters = computed(() => {
    return filters.foodTypes.length > 0 || 
           filters.priceRange[0] > 0 || 
           filters.priceRange[1] < 500 || 
           filters.minRating > 0 || 
           filters.distance > 0
  })
  
  // 获取美食类型标签
  const getFoodTypeLabel = (value) => {
    const option = foodTypeOptions.find(opt => opt.value === value)
    return option ? option.label : value
  }
  
  // 获取美食列表
  const fetchFoods = async () => {
    loading.value = true
    
    try {
      // 构建查询参数
      const params = new URLSearchParams()
      params.append('page', currentPage.value)
      params.append('size', pageSize.value)
      
      if (searchQuery.value) {
        params.append('q', searchQuery.value)
        // 添加到搜索历史
        recommendStore.addSearchHistory(searchQuery.value)
      }
      
      if (filters.foodTypes.length > 0) {
        filters.foodTypes.forEach(type => {
          params.append('types', type)
        })
      }
      
      if (filters.priceRange[0] > 0 || filters.priceRange[1] < 500) {
        params.append('minPrice', filters.priceRange[0])
        params.append('maxPrice', filters.priceRange[1])
      }
      
      if (filters.minRating > 0) {
        params.append('minRating', filters.minRating)
      }
      
      if (filters.distance > 0) {
        params.append('distance', filters.distance)
        
        // 如果设置了距离筛选，需要获取用户当前位置
        const { latitude, longitude } = await getCurrentPosition()
        params.append('lat', latitude)
        params.append('lng', longitude)
      }
      
      // 调用API获取美食列表
      const response = await fetch(`/api/foods?${params.toString()}`)
      
      if (!response.ok) {
        throw new Error('Failed to fetch foods')
      }
      
      const data = await response.json()
      foods.value = data.items
      totalItems.value = data.total
    } catch (err) {
      console.error('Error fetching foods:', err)
      ElMessage.error('获取美食列表失败，请稍后再试')
      foods.value = []
      totalItems.value = 0
    } finally {
      loading.value = false
    }
  }
  
  // 获取当前位置
  const getCurrentPosition = () => {
    return new Promise((resolve, reject) => {
      // 首先尝试使用用户在设置中保存的位置
      const savedLocation = settingsStore.mapSettings.defaultCenter
      if (savedLocation && savedLocation.lat && savedLocation.lng) {
        resolve({
          latitude: savedLocation.lat,
          longitude: savedLocation.lng
        })
        return
      }
      
      // 如果没有保存的位置，尝试获取当前位置
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            resolve({
              latitude: position.coords.latitude,
              longitude: position.coords.longitude
            })
          },
          (error) => {
            console.error('Error getting current position:', error)
            // 使用默认位置（北京）
            resolve({
              latitude: 39.9042,
              longitude: 116.4074
            })
          },
          { timeout: 10000 }
        )
      } else {
        console.error('Geolocation is not supported by this browser')
        // 使用默认位置（北京）
        resolve({
          latitude: 39.9042,
          longitude: 116.4074
        })
      }
    })
  }
  
  // 处理搜索
  const handleSearch = () => {
    currentPage.value = 1
    fetchFoods()
  }
  
  // 应用筛选条件
  const applyFilters = () => {
    showFilterDrawer.value = false
    currentPage.value = 1
    fetchFoods()
  }
  
  // 重置筛选条件
  const resetFilters = () => {
    searchQuery.value = ''
    filters.foodTypes = []
    filters.priceRange = [0, 500]
    filters.minRating = 0
    filters.distance = 0
    currentPage.value = 1
    fetchFoods()
  }
  
  // 移除单个筛选条件
  const removeFilter = (type, value) => {
    if (type === 'foodType') {
      filters.foodTypes = filters.foodTypes.filter(t => t !== value)
    } else if (type === 'priceRange') {
      filters.priceRange = [0, 500]
    } else if (type === 'minRating') {
      filters.minRating = 0
    } else if (type === 'distance') {
      filters.distance = 0
    }
    fetchFoods()
  }
  
  // 查看美食详情
  const viewFoodDetail = (id) => {
    router.push(`/food/${id}`)
  }
  
  // 处理分页大小变化
  const handleSizeChange = (size) => {
    pageSize.value = size
    fetchFoods()
  }
  
  // 处理页码变化
  const handleCurrentChange = (page) => {
    currentPage.value = page
    fetchFoods()
  }
  
  // 监听搜索查询变化
  watch(searchQuery, (newQuery, oldQuery) => {
    if (newQuery === '' && oldQuery !== '') {
      fetchFoods()
    }
  })
  
  // 组件挂载时获取数据
  onMounted(() => {
    fetchFoods()
  })
  </script>
  
  <style scoped>
  .food-recommend-container {
    padding-bottom: 40px;
  }
  
  .food-header {
    background-color: #409EFF;
    color: white;
    padding: 40px 0;
    margin-bottom: 30px;
    text-align: center;
  }
  
  .food-header h1 {
    font-size: 2rem;
    margin-bottom: 10px;
  }
  
  .food-header p {
    font-size: 1.1rem;
    opacity: 0.9;
  }
  
  .search-filter-container {
    margin-bottom: 20px;
  }
  
  .filter-drawer-content {
    padding: 20px;
  }
  
  .filter-drawer-content h3 {
    margin-top: 20px;
    margin-bottom: 10px;
    font-size: 16px;
    color: #303133;
  }
  
  .filter-actions {
    margin-top: 30px;
    display: flex;
    justify-content: space-between;
  }
  
  .active-filters {
    margin-bottom: 20px;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 10px;
  }
  
  .filter-label {
    color: #606266;
    margin-right: 5px;
  }
  
  .loading-container {
    padding: 20px 0;
  }
  
  .food-card {
    margin-bottom: 20px;
    cursor: pointer;
    transition: transform 0.3s;
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  
  .food-card:hover {
    transform: translateY(-5px);
  }
  
  .food-image {
    position: relative;
    height: 180px;
    overflow: hidden;
  }
  
  .food-image .el-image {
    width: 100%;
    height: 100%;
  }
  
  .food-price {
    position: absolute;
    bottom: 10px;
    right: 10px;
    background-color: rgba(0, 0, 0, 0.7);
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 14px;
  }
  
  .food-info {
    padding: 15px;
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  
  .food-name {
    margin: 0 0 10px;
    font-size: 16px;
    font-weight: 600;
    color: #303133;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .food-meta {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
  }
  
  .food-rating-value {
    margin-left: 5px;
    color: #ff9900;
    font-size: 14px;
  }
  
  .food-description {
    margin: 0 0 10px;
    color: #606266;
    font-size: 14px;
    line-height: 1.4;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
  }
  
  .food-tags {
    margin-bottom: 10px;
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
  }
  
  .restaurant-info {
    margin-top: auto;
    display: flex;
    align-items: center;
    color: #909399;
    font-size: 13px;
  }
  
  .restaurant-info i {
    margin-right: 5px;
  }
  
  .pagination-container {
    margin-top: 30px;
    display: flex;
    justify-content: center;
  }
  
  @media (max-width: 768px) {
    .food-header {
      padding: 30px 0;
    }
    
    .food-header h1 {
      font-size: 1.5rem;
    }
    
    .food-header p {
      font-size: 1rem;
    }
    
    .search-filter-container .el-button {
      margin-top: 10px;
    }
  }
  </style>