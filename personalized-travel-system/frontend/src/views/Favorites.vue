<template>
  <div class="favorites-container">
    <el-card class="favorites-card">
      <template #header>
        <div class="favorites-header">
          <h2>我的收藏</h2>
          <el-radio-group v-model="activeType" size="small">
            <el-radio-button label="places">景点</el-radio-button>
            <el-radio-button label="foods">美食</el-radio-button>
            <el-radio-button label="routes">路线</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="10" animated />
      </div>
      
      <div v-else>
        <!-- 景点收藏 -->
        <div v-if="activeType === 'places'" class="favorites-list">
          <el-empty v-if="placesList.length === 0" description="暂无收藏的景点"></el-empty>
          
          <el-row :gutter="20">
            <el-col v-for="place in placesList" :key="place.id" :xs="24" :sm="12" :md="8" :lg="8" :xl="6">
              <el-card class="favorite-item" shadow="hover" @click="viewPlaceDetail(place.id)">
                <img :src="place.image" class="favorite-image" alt="景点图片">
                <div class="favorite-info">
                  <h3>{{ place.name }}</h3>
                  <p class="location"><i class="el-icon-location"></i> {{ place.location }}</p>
                  <div class="rating">
                    <el-rate v-model="place.rating" disabled text-color="#ff9900"></el-rate>
                    <span>{{ place.rating.toFixed(1) }}</span>
                  </div>
                  <p class="description">{{ place.description }}</p>
                </div>
                <div class="favorite-actions">
                  <el-button type="danger" size="small" icon="el-icon-delete" circle
                    @click.stop="removeFavorite('places', place.id)"></el-button>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
        
        <!-- 美食收藏 -->
        <div v-if="activeType === 'foods'" class="favorites-list">
          <el-empty v-if="foodsList.length === 0" description="暂无收藏的美食"></el-empty>
          
          <el-row :gutter="20">
            <el-col v-for="food in foodsList" :key="food.id" :xs="24" :sm="12" :md="8" :lg="8" :xl="6">
              <el-card class="favorite-item" shadow="hover" @click="viewFoodDetail(food.id)">
                <img :src="food.image" class="favorite-image" alt="美食图片">
                <div class="favorite-info">
                  <h3>{{ food.name }}</h3>
                  <p class="location"><i class="el-icon-location"></i> {{ food.restaurant }}</p>
                  <div class="rating">
                    <el-rate v-model="food.rating" disabled text-color="#ff9900"></el-rate>
                    <span>{{ food.rating.toFixed(1) }}</span>
                  </div>
                  <p class="description">{{ food.description }}</p>
                </div>
                <div class="favorite-actions">
                  <el-button type="danger" size="small" icon="el-icon-delete" circle
                    @click.stop="removeFavorite('foods', food.id)"></el-button>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
        
        <!-- 路线收藏 -->
        <div v-if="activeType === 'routes'" class="favorites-list">
          <el-empty v-if="routesList.length === 0" description="暂无收藏的路线"></el-empty>
          
          <el-row :gutter="20">
            <el-col v-for="route in routesList" :key="route.id" :xs="24" :sm="12" :md="8" :lg="8" :xl="6">
              <el-card class="favorite-item" shadow="hover" @click="viewRouteDetail(route.id)">
                <img :src="route.image" class="favorite-image" alt="路线图片">
                <div class="favorite-info">
                  <h3>{{ route.name }}</h3>
                  <p class="duration"><i class="el-icon-time"></i> {{ route.duration }}</p>
                  <div class="rating">
                    <el-rate v-model="route.rating" disabled text-color="#ff9900"></el-rate>
                    <span>{{ route.rating.toFixed(1) }}</span>
                  </div>
                  <p class="description">{{ route.description }}</p>
                </div>
                <div class="favorite-actions">
                  <el-button type="danger" size="small" icon="el-icon-delete" circle
                    @click.stop="removeFavorite('routes', route.id)"></el-button>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '../store'

const router = useRouter()
const userStore = useUserStore()

// 检查用户是否登录
if (!userStore.isLoggedIn) {
  ElMessage.warning('请先登录')
  router.push('/login?redirect=/profile/favorites')
}

// 当前选中的收藏类型
const activeType = ref('places')

// 加载状态
const loading = ref(true)

// 收藏列表
const placesList = ref([])
const foodsList = ref([])
const routesList = ref([])

// 获取收藏数据
const fetchFavorites = async () => {
  loading.value = true
  
  try {
    // 模拟API请求
    // 实际项目中应该调用真实的API
    console.log('获取收藏数据，类型:', activeType.value)
    
    // 模拟延迟
    setTimeout(() => {
      // 模拟数据
      if (activeType.value === 'places') {
        placesList.value = [
          {
            id: 1,
            name: '西湖',
            location: '杭州市西湖区',
            image: 'https://example.com/xihu.jpg',
            rating: 4.8,
            description: '西湖，位于浙江省杭州市西湖区龙井路1号，杭州市区西部，景区总面积49平方千米，汇水面积为21.22平方千米，湖面面积为6.38平方千米。'
          },
          {
            id: 2,
            name: '故宫',
            location: '北京市东城区景山前街4号',
            image: 'https://example.com/gugong.jpg',
            rating: 4.9,
            description: '北京故宫是中国明清两代的皇家宫殿，旧称为紫禁城，位于北京中轴线的中心，是中国古代宫廷建筑之精华。'
          },
          {
            id: 3,
            name: '黄山',
            location: '安徽省黄山市黄山区汤口镇',
            image: 'https://example.com/huangshan.jpg',
            rating: 4.7,
            description: '黄山位于安徽省南部黄山市境内，有72峰，主峰莲花峰海拔1864米，与光明顶、天都峰并称三大黄山主峰。'
          }
        ]
      } else if (activeType.value === 'foods') {
        foodsList.value = [
          {
            id: 1,
            name: '西湖醋鱼',
            restaurant: '楼外楼',
            image: 'https://example.com/xihucuyu.jpg',
            rating: 4.6,
            description: '西湖醋鱼是浙江省杭州市的传统名菜，属于浙菜系。此菜选用西湖特产草鱼为主料，制作时保持鱼的完整，口味酸甜适中。'
          },
          {
            id: 2,
            name: '北京烤鸭',
            restaurant: '全聚德',
            image: 'https://example.com/kaoya.jpg',
            rating: 4.8,
            description: '北京烤鸭是具有世界声誉的北京著名菜式，用料为优质肥嫩的北京鸭，果木炭火烤制，色泽红艳，肉质细嫩。'
          }
        ]
      } else if (activeType.value === 'routes') {
        routesList.value = [
          {
            id: 1,
            name: '杭州西湖一日游',
            duration: '1天',
            image: 'https://example.com/xihu-route.jpg',
            rating: 4.5,
            description: '包含断桥残雪、平湖秋月、三潭印月等景点，体验西湖十景的精华。'
          },
          {
            id: 2,
            name: '北京故宫-颐和园经典线路',
            duration: '2天',
            image: 'https://example.com/beijing-route.jpg',
            rating: 4.7,
            description: '游览北京核心景区，感受古都文化底蕴，包含故宫、天安门、颐和园等景点。'
          }
        ]
      }
      
      loading.value = false
    }, 1000)
    
    // 实际API调用示例
    /*
    const response = await fetch(`/api/user/favorites/${activeType.value}`, {
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    })
    
    const data = await response.json()
    
    if (data.success) {
      if (activeType.value === 'places') {
        placesList.value = data.favorites
      } else if (activeType.value === 'foods') {
        foodsList.value = data.favorites
      } else if (activeType.value === 'routes') {
        routesList.value = data.favorites
      }
    } else {
      ElMessage.error(data.message || '获取收藏数据失败')
    }
    */
  } catch (error) {
    console.error('获取收藏数据时出错:', error)
    ElMessage.error('获取收藏数据失败')
  } finally {
    loading.value = false
  }
}

// 查看详情
const viewPlaceDetail = (id) => {
  router.push(`/place/${id}`)
}

const viewFoodDetail = (id) => {
  router.push(`/food/${id}`)
}

const viewRouteDetail = (id) => {
  router.push(`/route/${id}`)
}

// 移除收藏
const removeFavorite = async (type, id) => {
  try {
    // 确认删除
    await ElMessageBox.confirm('确定要取消收藏吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // 模拟API请求
    // 实际项目中应该调用真实的API
    console.log('移除收藏:', type, id)
    
    // 模拟成功响应
    setTimeout(() => {
      // 从列表中移除
      if (type === 'places') {
        placesList.value = placesList.value.filter(item => item.id !== id)
      } else if (type === 'foods') {
        foodsList.value = foodsList.value.filter(item => item.id !== id)
      } else if (type === 'routes') {
        routesList.value = routesList.value.filter(item => item.id !== id)
      }
      
      ElMessage.success('已取消收藏')
    }, 500)
    
    // 实际API调用示例
    /*
    const response = await fetch(`/api/user/favorites/${type}/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    })
    
    const data = await response.json()
    
    if (data.success) {
      // 从列表中移除
      if (type === 'places') {
        placesList.value = placesList.value.filter(item => item.id !== id)
      } else if (type === 'foods') {
        foodsList.value = foodsList.value.filter(item => item.id !== id)
      } else if (type === 'routes') {
        routesList.value = routesList.value.filter(item => item.id !== id)
      }
      
      ElMessage.success('已取消收藏')
    } else {
      ElMessage.error(data.message || '操作失败，请重试')
    }
    */
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消收藏时出错:', error)
      ElMessage.error('操作失败，请重试')
    }
  }
}

// 监听收藏类型变化
const handleTypeChange = () => {
  fetchFavorites()
}

// 监听activeType变化
watch(activeType, () => {
  handleTypeChange()
})

// 组件挂载时获取收藏数据
onMounted(() => {
  fetchFavorites()
})
</script>

<style scoped lang="scss">
.favorites-container {
  max-width: 1200px;
  margin: 20px auto;
  padding: 0 20px;
}

.favorites-card {
  margin-bottom: 30px;
}

.favorites-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  @media (max-width: 768px) {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}

.loading-container {
  padding: 20px 0;
}

.favorites-list {
  margin-top: 20px;
}

.favorite-item {
  margin-bottom: 20px;
  position: relative;
  overflow: hidden;
  transition: transform 0.3s;
  
  &:hover {
    transform: translateY(-5px);
  }
}

.favorite-image {
  width: 100%;
  height: 180px;
  object-fit: cover;
  border-radius: 4px;
}

.favorite-info {
  padding: 10px 0;
  
  h3 {
    margin: 0 0 8px;
    font-size: 18px;
    font-weight: bold;
  }
  
  .location, .duration {
    margin: 5px 0;
    font-size: 14px;
    color: #606266;
    
    i {
      margin-right: 5px;
    }
  }
  
  .rating {
    display: flex;
    align-items: center;
    margin: 8px 0;
    
    span {
      margin-left: 8px;
      color: #ff9900;
    }
  }
  
  .description {
    margin: 8px 0 0;
    font-size: 14px;
    color: #606266;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
  }
}

.favorite-actions {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 10;
  opacity: 0;
  transition: opacity 0.3s;
  
  .favorite-item:hover & {
    opacity: 1;
  }
}
</style>