<template>
    <div class="place-detail-container">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="10" animated />
      </div>
      
      <!-- 错误提示 -->
      <el-empty v-else-if="error" description="加载失败，请稍后再试">
        <el-button type="primary" @click="fetchPlaceDetail">重试</el-button>
      </el-empty>
      
      <!-- 景点详情内容 -->
      <template v-else-if="place">
        <!-- 景点头部信息 -->
        <div class="place-header" :style="{ backgroundImage: `url(${place.coverImage || '@/assets/default-place.jpg'})` }">
          <div class="place-header-overlay">
            <div class="container">
              <h1>{{ place.name }}</h1>
              <div class="place-meta">
                <span class="place-type">{{ place.type }}</span>
                <span class="place-rating">
                  <el-rate v-model="place.rating" disabled text-color="#ff9900" />
                  <span>{{ place.rating.toFixed(1) }}</span>
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 景点主体内容 -->
        <div class="container place-content">
          <el-row :gutter="20">
            <!-- 左侧主要内容 -->
            <el-col :xs="24" :sm="24" :md="16">
              <!-- 景点简介 -->
              <el-card class="place-section">
                <template #header>
                  <div class="card-header">
                    <h2>景点简介</h2>
                  </div>
                </template>
                <div class="place-description">
                  <p>{{ place.description }}</p>
                </div>
              </el-card>
              
              <!-- 景点图片 -->
              <el-card class="place-section">
                <template #header>
                  <div class="card-header">
                    <h2>景点图片</h2>
                  </div>
                </template>
                <div class="place-gallery">
                  <el-image 
                    v-for="(img, index) in place.images" 
                    :key="index"
                    :src="img"
                    fit="cover"
                    :preview-src-list="place.images"
                    class="gallery-image"
                  />
                </div>
              </el-card>
              
              <!-- 用户评价 -->
              <el-card class="place-section">
                <template #header>
                  <div class="card-header">
                    <h2>用户评价</h2>
                  </div>
                </template>
                <div class="place-reviews">
                  <div v-if="place.reviews && place.reviews.length > 0">
                    <div v-for="(review, index) in place.reviews" :key="index" class="review-item">
                      <div class="review-header">
                        <el-avatar :size="40" :src="review.userAvatar">{{ review.userName.charAt(0) }}</el-avatar>
                        <div class="review-user-info">
                          <h4>{{ review.userName }}</h4>
                          <div class="review-meta">
                            <el-rate v-model="review.rating" disabled size="small" />
                            <span class="review-date">{{ formatDate(review.date) }}</span>
                          </div>
                        </div>
                      </div>
                      <div class="review-content">
                        <p>{{ review.content }}</p>
                      </div>
                    </div>
                  </div>
                  <el-empty v-else description="暂无评价" />
                  
                  <!-- 添加评价 -->
                  <div class="add-review" v-if="isLoggedIn">
                    <h3>添加您的评价</h3>
                    <el-form :model="reviewForm" @submit.prevent="submitReview">
                      <el-form-item label="评分">
                        <el-rate v-model="reviewForm.rating" />
                      </el-form-item>
                      <el-form-item label="评价内容">
                        <el-input 
                          v-model="reviewForm.content" 
                          type="textarea" 
                          :rows="4" 
                          placeholder="分享您的游览体验..."
                        />
                      </el-form-item>
                      <el-form-item>
                        <el-button type="primary" native-type="submit" :loading="submitting">提交评价</el-button>
                      </el-form-item>
                    </el-form>
                  </div>
                  <el-alert 
                    v-else 
                    title="请登录后添加评价" 
                    type="info" 
                    :closable="false"
                    show-icon
                  >
                    <template #default>
                      <router-link to="/login">立即登录</router-link>
                    </template>
                  </el-alert>
                </div>
              </el-card>
            </el-col>
            
            <!-- 右侧信息栏 -->
            <el-col :xs="24" :sm="24" :md="8">
              <!-- 基本信息 -->
              <el-card class="place-section">
                <template #header>
                  <div class="card-header">
                    <h2>基本信息</h2>
                  </div>
                </template>
                <ul class="info-list">
                  <li>
                    <i class="el-icon-location"></i>
                    <span>地址：{{ place.address }}</span>
                  </li>
                  <li>
                    <i class="el-icon-time"></i>
                    <span>开放时间：{{ place.openingHours }}</span>
                  </li>
                  <li>
                    <i class="el-icon-money"></i>
                    <span>门票价格：{{ place.ticketPrice ? `¥${place.ticketPrice}` : '免费' }}</span>
                  </li>
                  <li>
                    <i class="el-icon-phone"></i>
                    <span>联系电话：{{ place.contactPhone || '暂无' }}</span>
                  </li>
                </ul>
                
                <div class="action-buttons">
                  <el-button type="primary" icon="el-icon-map-location" @click="navigateToPlace">导航前往</el-button>
                  <el-button 
                    :type="isFavorite ? 'danger' : 'default'" 
                    :icon="isFavorite ? 'el-icon-star-on' : 'el-icon-star-off'" 
                    @click="toggleFavorite"
                  >
                    {{ isFavorite ? '取消收藏' : '收藏' }}
                  </el-button>
                </div>
              </el-card>
              
              <!-- 地图位置 -->
              <el-card class="place-section">
                <template #header>
                  <div class="card-header">
                    <h2>地图位置</h2>
                  </div>
                </template>
                <div class="place-map" ref="mapContainer"></div>
              </el-card>
              
              <!-- 周边推荐 -->
              <el-card class="place-section">
                <template #header>
                  <div class="card-header">
                    <h2>周边推荐</h2>
                  </div>
                </template>
                <div class="nearby-places">
                  <div v-if="nearbyPlaces.length > 0">
                    <router-link 
                      v-for="nearby in nearbyPlaces" 
                      :key="nearby.id"
                      :to="`/place/${nearby.id}`"
                      class="nearby-place-item"
                    >
                      <el-image :src="nearby.coverImage || '@/assets/default-place.jpg'" fit="cover" />
                      <div class="nearby-place-info">
                        <h4>{{ nearby.name }}</h4>
                        <div class="nearby-place-meta">
                          <span>{{ nearby.distance }}km</span>
                          <el-rate v-model="nearby.rating" disabled size="small" />
                        </div>
                      </div>
                    </router-link>
                  </div>
                  <el-empty v-else description="暂无周边推荐" />
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </template>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive, computed, onMounted, watch } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import { useUserStore, useRecommendStore } from '../store'
  
  // 路由相关
  const route = useRoute()
  const router = useRouter()
  const placeId = computed(() => route.params.id)
  
  // 状态管理
  const userStore = useUserStore()
  const recommendStore = useRecommendStore()
  
  // 用户登录状态
  const isLoggedIn = computed(() => userStore.isLoggedIn)
  
  // 页面状态
  const loading = ref(true)
  const error = ref(false)
  const place = ref(null)
  const nearbyPlaces = ref([])
  const isFavorite = ref(false)
  const submitting = ref(false)
  
  // 地图容器引用
  const mapContainer = ref(null)
  
  // 评价表单
  const reviewForm = reactive({
    rating: 5,
    content: ''
  })
  
  // 获取景点详情
  const fetchPlaceDetail = async () => {
    loading.value = true
    error.value = false
    
    try {
      // 调用API获取景点详情
      const response = await fetch(`/api/places/${placeId.value}`)
      
      if (!response.ok) {
        throw new Error('Failed to fetch place details')
      }
      
      const data = await response.json()
      place.value = data
      
      // 添加到最近浏览
      if (place.value) {
        recommendStore.addRecentPlace(place.value)
      }
      
      // 检查是否已收藏
      checkFavoriteStatus()
      
      // 获取周边景点
      fetchNearbyPlaces()
      
      // 初始化地图
      initMap()
    } catch (err) {
      console.error('Error fetching place details:', err)
      error.value = true
    } finally {
      loading.value = false
    }
  }
  
  // 获取周边景点
  const fetchNearbyPlaces = async () => {
    if (!place.value || !place.value.location) return
    
    try {
      const { latitude, longitude } = place.value.location
      const response = await fetch(`/api/places/nearby?lat=${latitude}&lng=${longitude}&exclude=${placeId.value}`)
      
      if (!response.ok) {
        throw new Error('Failed to fetch nearby places')
      }
      
      const data = await response.json()
      nearbyPlaces.value = data.slice(0, 5) // 最多显示5个
    } catch (err) {
      console.error('Error fetching nearby places:', err)
      nearbyPlaces.value = []
    }
  }
  
  // 检查收藏状态
  const checkFavoriteStatus = async () => {
    if (!isLoggedIn.value || !placeId.value) return
    
    try {
      const response = await fetch(`/api/user/favorites/check?placeId=${placeId.value}`, {
        headers: {
          'Authorization': `Bearer ${userStore.token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        isFavorite.value = data.isFavorite
      }
    } catch (err) {
      console.error('Error checking favorite status:', err)
    }
  }
  
  // 切换收藏状态
  const toggleFavorite = async () => {
    if (!isLoggedIn.value) {
      ElMessage.warning('请先登录')
      router.push('/login')
      return
    }
    
    try {
      const method = isFavorite.value ? 'DELETE' : 'POST'
      const response = await fetch(`/api/user/favorites`, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${userStore.token}`
        },
        body: JSON.stringify({ placeId: placeId.value })
      })
      
      if (response.ok) {
        isFavorite.value = !isFavorite.value
        ElMessage.success(isFavorite.value ? '已添加到收藏' : '已取消收藏')
      } else {
        throw new Error('操作失败')
      }
    } catch (err) {
      console.error('Error toggling favorite:', err)
      ElMessage.error('操作失败，请稍后再试')
    }
  }
  
  // 提交评价
  const submitReview = async () => {
    if (!isLoggedIn.value) {
      ElMessage.warning('请先登录')
      return
    }
    
    if (reviewForm.content.trim() === '') {
      ElMessage.warning('请输入评价内容')
      return
    }
    
    submitting.value = true
    
    try {
      const response = await fetch(`/api/places/${placeId.value}/reviews`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${userStore.token}`
        },
        body: JSON.stringify({
          rating: reviewForm.rating,
          content: reviewForm.content
        })
      })
      
      if (response.ok) {
        ElMessage.success('评价提交成功')
        reviewForm.content = ''
        // 重新获取景点详情，更新评价列表
        fetchPlaceDetail()
      } else {
        throw new Error('评价提交失败')
      }
    } catch (err) {
      console.error('Error submitting review:', err)
      ElMessage.error('评价提交失败，请稍后再试')
    } finally {
      submitting.value = false
    }
  }
  
  // 导航到景点
  const navigateToPlace = () => {
    if (!place.value || !place.value.location) {
      ElMessage.warning('无法获取景点位置信息')
      return
    }
    
    const { latitude, longitude } = place.value.location
    router.push(`/map?lat=${latitude}&lng=${longitude}&name=${encodeURIComponent(place.value.name)}`)
  }
  
  // 初始化地图
  const initMap = () => {
    if (!place.value || !place.value.location || !mapContainer.value) return
    
    // 这里应该集成地图API，如高德地图、百度地图等
    // 以下为示例代码，实际实现需要根据使用的地图API调整
    setTimeout(() => {
      const mapElement = mapContainer.value
      mapElement.innerHTML = `<div class="map-placeholder">地图加载中...<br>位置: ${place.value.location.latitude}, ${place.value.location.longitude}</div>`
    }, 100)
  }
  
  // 格式化日期
  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
  }
  
  // 监听路由参数变化，重新获取数据
  watch(() => route.params.id, (newId, oldId) => {
    if (newId !== oldId) {
      fetchPlaceDetail()
    }
  })
  
  // 组件挂载时获取数据
  onMounted(() => {
    fetchPlaceDetail()
  })
  </script>
  
  <style scoped>
  .place-detail-container {
    padding-bottom: 40px;
  }
  
  .loading-container {
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
  }
  
  .place-header {
    height: 300px;
    background-size: cover;
    background-position: center;
    position: relative;
    margin-bottom: 30px;
  }
  
  .place-header-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(to bottom, rgba(0,0,0,0.2), rgba(0,0,0,0.7));
    display: flex;
    align-items: flex-end;
    padding-bottom: 30px;
  }
  
  .place-header h1 {
    color: white;
    font-size: 2.5rem;
    margin-bottom: 10px;
  }
  
  .place-meta {
    display: flex;
    align-items: center;
    color: white;
  }
  
  .place-type {
    background-color: rgba(255, 255, 255, 0.2);
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 14px;
    margin-right: 15px;
  }
  
  .place-rating {
    display: flex;
    align-items: center;
  }
  
  .place-rating span {
    margin-left: 8px;
  }
  
  .place-content {
    max-width: 1200px;
    margin: 0 auto;
  }
  
  .place-section {
    margin-bottom: 20px;
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .card-header h2 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
  }
  
  .place-description p {
    line-height: 1.6;
    color: #606266;
  }
  
  .place-gallery {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 10px;
  }
  
  .gallery-image {
    height: 120px;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .info-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  
  .info-list li {
    display: flex;
    align-items: flex-start;
    margin-bottom: 15px;
    color: #606266;
  }
  
  .info-list li i {
    margin-right: 10px;
    color: #409EFF;
    font-size: 18px;
  }
  
  .action-buttons {
    display: flex;
    gap: 10px;
    margin-top: 20px;
  }
  
  .place-map {
    height: 200px;
    background-color: #f5f7fa;
    border-radius: 4px;
  }
  
  .map-placeholder {
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
    color: #909399;
    font-size: 14px;
    line-height: 1.5;
  }
  
  .nearby-places {
    display: flex;
    flex-direction: column;
    gap: 15px;
  }
  
  .nearby-place-item {
    display: flex;
    text-decoration: none;
    color: inherit;
    border-bottom: 1px solid #ebeef5;
    padding-bottom: 15px;
  }
  
  .nearby-place-item:last-child {
    border-bottom: none;
  }
  
  .nearby-place-item .el-image {
    width: 80px;
    height: 60px;
    border-radius: 4px;
    margin-right: 10px;
  }
  
  .nearby-place-info {
    flex: 1;
  }
  
  .nearby-place-info h4 {
    margin: 0 0 5px;
    font-size: 14px;
    color: #303133;
  }
  
  .nearby-place-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    color: #909399;
  }
  
  .review-item {
    margin-bottom: 20px;
    padding-bottom: 20px;
    border-bottom: 1px solid #ebeef5;
  }
  
  .review-item:last-child {
    border-bottom: none;
  }
  
  .review-header {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
  }
  
  .review-user-info {
    margin-left: 10px;
  }
  
  .review-user-info h4 {
    margin: 0 0 5px;
    font-size: 14px;
  }
  
  .review-meta {
    display: flex;
    align-items: center;
  }
  
  .review-date {
    margin-left: 10px;
    font-size: 12px;
    color: #909399;
  }
  
  .review-content p {
    margin: 0;
    color: #606266;
    line-height: 1.6;
  }
  
  .add-review {
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px dashed #ebeef5;
  }
  
  .add-review h3 {
    margin-top: 0;
    margin-bottom: 20px;
    font-size: 16px;
  }
  
  @media (max-width: 768px) {
    .place-header {
      height: 200px;
    }
    
    .place-header h1 {
      font-size: 1.8rem;
    }
    
    .gallery-image {
      height: 100px;
    }
  }
  </style>