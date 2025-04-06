<template>
    <div class="map-view-container">
      <!-- 地图容器 -->
      <div class="map-container" ref="mapContainer"></div>
      
      <!-- 侧边栏 -->
      <div class="sidebar" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
        <div class="sidebar-toggle" @click="toggleSidebar">
          <i :class="sidebarCollapsed ? 'el-icon-arrow-right' : 'el-icon-arrow-left'"></i>
        </div>
        
        <div class="sidebar-content">
          <el-tabs v-model="activeTab">
            <!-- 搜索标签页 -->
            <el-tab-pane label="搜索" name="search">
              <div class="search-panel">
                <el-input
                  v-model="searchQuery"
                  placeholder="搜索景点、地址或坐标"
                  prefix-icon="el-icon-search"
                  clearable
                  @keyup.enter="handleSearch"
                >
                  <template #append>
                    <el-button @click="handleSearch">搜索</el-button>
                  </template>
                </el-input>
                
                <div class="search-history" v-if="searchHistory.length > 0">
                  <div class="search-history-header">
                    <h4>搜索历史</h4>
                    <el-button type="text" @click="clearSearchHistory">清空</el-button>
                  </div>
                  <div class="search-history-list">
                    <el-tag
                      v-for="(item, index) in searchHistory"
                      :key="index"
                      size="small"
                      @click="searchQuery = item; handleSearch()"
                    >
                      {{ item }}
                    </el-tag>
                  </div>
                </div>
                
                <div class="search-results" v-if="searchResults.length > 0">
                  <h4>搜索结果</h4>
                  <el-scrollbar height="calc(100vh - 300px)">
                    <div
                      v-for="(result, index) in searchResults"
                      :key="index"
                      class="search-result-item"
                      @click="selectSearchResult(result)"
                    >
                      <div class="result-icon">
                        <i :class="getResultIcon(result.type)"></i>
                      </div>
                      <div class="result-info">
                        <h5>{{ result.name }}</h5>
                        <p>{{ result.address }}</p>
                      </div>
                    </div>
                  </el-scrollbar>
                </div>
                
                <el-empty v-else-if="searchPerformed && !loading" description="未找到结果" />
              </div>
            </el-tab-pane>
            
            <!-- 路线标签页 -->
            <el-tab-pane label="路线" name="route">
              <div class="route-panel">
                <div class="route-inputs">
                  <el-input
                    v-model="routeStart"
                    placeholder="起点"
                    prefix-icon="el-icon-position"
                    clearable
                  >
                    <template #append>
                      <el-button @click="setCurrentLocationAsStart">
                        <i class="el-icon-aim"></i>
                      </el-button>
                    </template>
                  </el-input>
                  
                  <div class="route-waypoints" v-if="waypoints.length > 0">
                    <div 
                      v-for="(waypoint, index) in waypoints" 
                      :key="index"
                      class="waypoint-item"
                    >
                      <el-input
                        v-model="waypoints[index]"
                        :placeholder="`途经点 ${index + 1}`"
                        prefix-icon="el-icon-location-information"
                        clearable
                        @clear="removeWaypoint(index)"
                      />
                      <el-button 
                        type="danger" 
                        icon="el-icon-delete" 
                        circle 
                        size="mini"
                        @click="removeWaypoint(index)"
                      />
                    </div>
                  </div>
                  
                  <div class="add-waypoint">
                    <el-button 
                      type="text" 
                      icon="el-icon-plus" 
                      @click="addWaypoint"
                      :disabled="waypoints.length >= 5"
                    >
                      添加途经点
                    </el-button>
                  </div>
                  
                  <el-input
                    v-model="routeEnd"
                    placeholder="终点"
                    prefix-icon="el-icon-location"
                    clearable
                  />
                </div>
                
                <div class="route-options">
                  <el-radio-group v-model="routeMode">
                    <el-radio-button label="driving">驾车</el-radio-button>
                    <el-radio-button label="walking">步行</el-radio-button>
                    <el-radio-button label="transit">公交</el-radio-button>
                    <el-radio-button label="riding">骑行</el-radio-button>
                  </el-radio-group>
                  
                  <el-button type="primary" @click="calculateRoute" :loading="routeLoading">
                    规划路线
                  </el-button>
                </div>
                
                <!-- 路线结果 -->
                <div class="route-results" v-if="routeResult">
                  <div class="route-summary">
                    <div class="route-info">
                      <div class="route-distance">
                        <i class="el-icon-odometer"></i>
                        <span>{{ routeResult.distance }}</span>
                      </div>
                      <div class="route-duration">
                        <i class="el-icon-time"></i>
                        <span>{{ routeResult.duration }}</span>
                      </div>
                    </div>
                    <el-button type="text" @click="clearRoute">清除路线</el-button>
                  </div>
                  
                  <el-collapse v-model="activeRouteSteps">
                    <el-collapse-item title="路线详情" name="steps">
                      <el-steps direction="vertical" :active="999">
                        <el-step 
                          v-for="(step, index) in routeResult.steps" 
                          :key="index"
                          :title="step.instruction"
                          :description="step.distance + ' · ' + step.duration"
                          @click="focusRouteStep(step)"
                        />
                      </el-steps>
                    </el-collapse-item>
                  </el-collapse>
                </div>
              </div>
            </el-tab-pane>
            
            <!-- 图层标签页 -->
            <el-tab-pane label="图层" name="layers">
              <div class="layers-panel">
                <h4>地图类型</h4>
                <el-radio-group v-model="mapType" @change="changeMapType">
                  <el-radio-button label="normal">普通地图</el-radio-button>
                  <el-radio-button label="satellite">卫星地图</el-radio-button>
                </el-radio-group>
                
                <h4>地图控件</h4>
                <el-checkbox v-model="showTraffic" @change="toggleTraffic">实时路况</el-checkbox>
                <el-checkbox v-model="showPOI" @change="togglePOI">兴趣点</el-checkbox>
                
                <h4>景点分类</h4>
                <el-checkbox-group v-model="visiblePlaceTypes" @change="updateVisiblePlaces">
                  <el-checkbox v-for="type in placeTypeOptions" :key="type.value" :label="type.value">
                    {{ type.label }}
                  </el-checkbox>
                </el-checkbox-group>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
      
      <!-- 地图控件 -->
      <div class="map-controls">
        <el-button-group>
          <el-button icon="el-icon-plus" circle @click="zoomIn"></el-button>
          <el-button icon="el-icon-minus" circle @click="zoomOut"></el-button>
        </el-button-group>
        <el-button icon="el-icon-aim" circle @click="locateUser"></el-button>
      </div>
      
      <!-- 景点信息卡片 -->
      <div class="place-info-card" v-if="selectedPlace" :style="{ bottom: selectedPlace ? '20px' : '-200px' }">
        <div class="place-card-header">
          <h3>{{ selectedPlace.name }}</h3>
          <el-button type="text" icon="el-icon-close" @click="closeSelectedPlace"></el-button>
        </div>
        <div class="place-card-content">
          <div class="place-card-image">
            <el-image :src="selectedPlace.image || '@/assets/default-place.jpg'" fit="cover" />
          </div>
          <div class="place-card-info">
            <div class="place-card-rating">
              <el-rate v-model="selectedPlace.rating" disabled text-color="#ff9900" />
              <span>{{ selectedPlace.rating.toFixed(1) }}</span>
            </div>
            <p class="place-card-address">
              <i class="el-icon-location"></i>
              <span>{{ selectedPlace.address }}</span>
            </p>
            <p class="place-card-description">{{ selectedPlace.description }}</p>
          </div>
        </div>
        <div class="place-card-actions">
          <el-button type="primary" size="small" @click="viewPlaceDetail(selectedPlace.id)">查看详情</el-button>
          <el-button size="small" @click="setAsRouteStart(selectedPlace)">设为起点</el-button>
          <el-button size="small" @click="setAsRouteEnd(selectedPlace)">设为终点</el-button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import { useUserStore, useRecommendStore, useSettingsStore } from '../store'
  
  // 路由相关
  const router = useRouter()
  const route = useRoute()
  
  // 状态管理
  const userStore = useUserStore()
  const recommendStore = useRecommendStore()
  const settingsStore = useSettingsStore()
  
  // 地图相关引用
  const mapContainer = ref(null)
  let map = null // 地图实例
  let markers = [] // 标记点数组
  let routePolyline = null // 路线折线
  
  // 侧边栏状态
  const sidebarCollapsed = ref(false)
  const activeTab = ref('search')
  
  // 搜索相关
  const searchQuery = ref('')
  const searchResults = ref([])
  const searchPerformed = ref(false)
  const loading = ref(false)
  const searchHistory = computed(() => recommendStore.searchHistory)
  
  // 路线规划相关
  const routeStart = ref('')
  const routeEnd = ref('')
  const waypoints = ref([])
  const routeMode = ref('driving')
  const routeLoading = ref(false)
  const routeResult = ref(null)
  const activeRouteSteps = ref(['steps'])
  
  // 地图设置
  const mapType = ref('normal')
  const showTraffic = ref(false)
  const showPOI = ref(true)
  
  // 景点分类
  const placeTypeOptions = [
    { label: '自然风光', value: 'nature' },
    { label: '历史古迹', value: 'historical' },
    { label: '博物馆', value: 'museum' },
    { label: '主题公园', value: 'theme_park' },
    { label: '宗教场所', value: 'religious' },
    { label: '城市地标', value: 'landmark' }
  ]
  const visiblePlaceTypes = ref(placeTypeOptions.map(type => type.value))
  
  // 选中的景点
  const selectedPlace = ref(null)
  
  // 切换侧边栏
  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
    // 调整地图大小以适应新的布局
    setTimeout(() => {
      if (map) {
        map.resize()
      }
    }, 300)
  }
  
  // 处理搜索
  const handleSearch = async () => {
    if (!searchQuery.value.trim()) return
    
    loading.value = true
    searchPerformed.value = true
    
    try {
      // 调用搜索API
      const response = await fetch(`/api/map/search?q=${encodeURIComponent(searchQuery.value)}`)
      
      if (!response.ok) {
        throw new Error('Search failed')
      }
      
      const data = await response.json()
      searchResults.value = data
      
      // 添加到搜索历史
      recommendStore.addSearchHistory(searchQuery.value)
      
      // 在地图上显示搜索结果
      showSearchResultsOnMap(data)
    } catch (err) {
      console.error('Error searching:', err)
      ElMessage.error('搜索失败，请稍后再试')
      searchResults.value = []
    } finally {
      loading.value = false
    }
  }
  
  // 清空搜索历史
  const clearSearchHistory = () => {
    recommendStore.clearSearchHistory()
  }
  
  // 选择搜索结果
  const selectSearchResult = (result) => {
    // 在地图上聚焦到选中的结果
    if (map && result.location) {
      map.flyTo({
        center: [result.location.longitude, result.location.latitude],
        zoom: 15,
        essential: true
      })
      
      // 如果是景点，显示景点信息卡片
      if (result.type === 'place') {
        selectedPlace.value = result
      }
    }
  }
  
  // 获取结果图标
  const getResultIcon = (type) => {
    switch (type) {
      case 'place': return 'el-icon-place'
      case 'address': return 'el-icon-location-information'
      case 'coordinate': return 'el-icon-coordinate'
      default: return 'el-icon-location'
    }
  }
  
  // 在地图上显示搜索结果
  const showSearchResultsOnMap = (results) => {
    // 清除现有标记
    clearMarkers()
    
    if (!map || results.length === 0) return
    
    // 创建边界框以包含所有结果
    const bounds = new mapboxgl.LngLatBounds()
    
    // 为每个结果添加标记
    results.forEach(result => {
      if (result.location) {
        const { longitude, latitude } = result.location
        
        // 创建标记
        const marker = new mapboxgl.Marker({
          color: '#409EFF'
        })
          .setLngLat([longitude, latitude])
          .addTo(map)
        
        // 添加点击事件
        marker.getElement().addEventListener('click', () => {
          selectedPlace.value = result
        })
        
        // 添加到标记数组
        markers.push(marker)
        
        // 扩展边界框
        bounds.extend([longitude, latitude])
      }
    })
    
    // 调整地图视图以包含所有标记
    if (!bounds.isEmpty()) {
      map.fitBounds(bounds, {
        padding: 50,
        maxZoom: 15
      })
    }
  }
  
  // 添加途经点
  const addWaypoint = () => {
    if (waypoints.value.length < 5) {
      waypoints.value.push('')
    }
  }
  
  // 移除途经点
  const removeWaypoint = (index) => {
    waypoints.value.splice(index, 1)
  }
  
  // 设置当前位置为起点
  const setCurrentLocationAsStart = async () => {
    try {
      const position = await getCurrentPosition()
      routeStart.value = `${position.latitude},${position.longitude}`
      ElMessage.success('已设置当前位置为起点')
    } catch (err) {
      ElMessage.error('无法获取当前位置')
    }
  }
  
  // 计算路线
  const calculateRoute = async () => {
    if (!routeStart.value || !routeEnd.value) {
      ElMessage.warning('请输入起点和终点')
      return
    }
    
    routeLoading.value = true
    
    try {
      // 构建API请求参数
      const params = new URLSearchParams()
      params.append('origin', routeStart.value)
      params.append('destination', routeEnd.value)
      params.append('mode', routeMode.value)
      
      // 添加途经点
      const validWaypoints = waypoints.value.filter(wp => wp.trim() !== '')
      if (validWaypoints.length > 0) {
        params.append('waypoints', validWaypoints.join('|'))
      }
      
      // 调用路线规划API
      const response = await fetch(`/api/map/route?${params.toString()}`)
      
      if (!response.ok) {
        throw new Error('Route calculation failed')
      }
      
      const data = await response.json()
      routeResult.value = data
      
      // 在地图上显示路线
      showRouteOnMap(data)
      
      // 切换到路线详情
      activeRouteSteps.value = ['steps']
    } catch (err) {
      console.error('Error calculating route:', err)
      ElMessage.error('路线规划失败，请稍后再试')
    } finally {
      routeLoading.value = false
    }
  }
  
  // 在地图上显示路线
  const showRouteOnMap = (routeData) => {
    // 清除现有路线
    clearRoute()
    
    if (!map || !routeData || !routeData.path) return
    
    // 创建路线折线
    routePolyline = new mapboxgl.Polyline({
      path: routeData.path,
      strokeColor: '#409EFF',
      strokeWeight: 6,
      strokeOpacity: 0.8
    }).addTo(map)
    
    // 调整地图视图以显示整个路线
    map.fitBounds(routeData.bounds, {
      padding: 50
    })
  }
  
  // 聚焦到路线步骤
  const focusRouteStep = (step) => {
    if (!map || !step.location) return
    
    map.flyTo({
      center: [step.location.longitude, step.location.latitude],
      zoom: 16,
      essential: true
    })
  }
  
  // 清除路线
  const clearRoute = () => {
    if (routePolyline) {
      routePolyline.remove()
      routePolyline = null
    }
    
    routeResult.value = null
  }
  
  // 更改地图类型
  const changeMapType = () => {
    if (!map) return
    
    map.setMapType(mapType.value)
  }
  
  // 切换交通图层
  const toggleTraffic = () => {
    if (!map) return
    
    if (showTraffic.value) {
      map.showTraffic()
    } else {
      map.hideTraffic()
    }
  }
  
  // 切换POI图层
  const togglePOI = () => {
    if (!map) return
    
    if (showPOI.value) {
      map.showPOI()
    } else {
      map.hidePOI()
    }
  }
  
  // 更新可见景点类型
  const updateVisiblePlaces = () => {
    // 重新加载景点数据
    loadPlaces()
  }
  
  // 放大地图
  const zoomIn = () => {
    if (map) {
      const currentZoom = map.getZoom()
      map.zoomTo(currentZoom + 1)
    }
  }
  
  // 缩小地图
  const zoomOut = () => {
    if (map) {
      const currentZoom = map.getZoom()
      map.zoomTo(currentZoom - 1)
    }
  }
  
  // 定位用户
  const locateUser = async () => {
    try {
      const position = await getCurrentPosition()
      
      if (map) {
        map.flyTo({
          center: [position.longitude, position.latitude],
          zoom: 15,
          essential: true
        })
        
        // 添加用户位置标记
        new mapboxgl.Marker({
          color: '#ff4500',
          element: createUserLocationMarker()
        })
          .setLngLat([position.longitude, position.latitude])
          .addTo(map)
      }
    } catch (err) {
      ElMessage.error('无法获取当前位置')
    }
  }
  
  // 创建用户位置标记元素
  const createUserLocationMarker = () => {
    const el = document.createElement('div')
    el.className = 'user-location-marker'
    el.innerHTML = '<div class="pulse"></div>'
    return el
  }
  
  // 关闭选中的景点
  const closeSelectedPlace = () => {
    selectedPlace.value = null
  }
  
  // 查看景点详情
  const viewPlaceDetail = (id) => {
    router.push(`/place/${id}`)
  }
  
  // 设置为路线起点
  const setAsRouteStart = (place) => {
    if (place && place.location) {
      routeStart.value = `${place.location.latitude},${place.location.longitude}`
      activeTab.value = 'route'
      ElMessage.success(`已设置 ${place.name} 为起点`)
    }
  }
  
  // 设置为路线终点
  const setAsRouteEnd = (place) => {
    if (place && place.location) {
      routeEnd.value = `${place.location.latitude},${place.location.longitude}`
      activeTab.value = 'route'
      ElMessage.success(`已设置 ${place.name} 为终点`)
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
            reject(error)
          },
          { timeout: 10000 }
        )
      } else {
        reject(new Error('Geolocation is not supported by this browser'))
      }
    })
  }
  
  // 加载景点数据
  const loadPlaces = async () => {
    try {
      // 构建API请求参数
      const params = new URLSearchParams()
      
      if (visiblePlaceTypes.value.length > 0) {
        visiblePlaceTypes.value.forEach(type => {
          params.append('types', type)
        })
      }
      
      // 如果地图已经初始化，添加当前视图范围
      if (map) {
        const bounds = map.getBounds()
        params.append('bounds', `${bounds.getSouthWest().lng},${bounds.getSouthWest().lat},${bounds.getNorthEast().lng},${bounds.getNorthEast().lat}`)
      }
      
      // 调用API获取景点数据
      const response = await fetch(`/api/places/map?${params.toString()}`)
      
      if (!response.ok) {
        throw new Error('Failed to fetch places')
      }
      
      const data = await response.json()
      
      // 清除现有标记
      clearMarkers()
      
      // 添加景点标记
      data.forEach(place => {
        if (place.location) {
          const { longitude, latitude } = place.location
          
          // 创建标记
          const marker = new mapboxgl.Marker({
            color: getMarkerColorByType(place.type)
          })
            .setLngLat([longitude, latitude])
            .addTo(map)
          
          // 添加点击事件
          marker.getElement().addEventListener('click', () => {
            selectedPlace.value = place
          })
          
          // 添加到标记数组
          markers.push(marker)
        }
      })
    } catch (err) {
      console.error('Error loading places:', err)
    }
  }
  
  // 根据景点类型获取标记颜色
  const getMarkerColorByType = (type) => {
    switch (type) {
      case 'nature': return '#4CAF50' // 绿色
      case 'historical': return '#FFC107' // 黄色
      case 'museum': return '#9C27B0' // 紫色
      case 'theme_park': return '#FF5722' // 橙色
      case 'religious': return '#2196F3' // 蓝色
      case 'landmark': return '#F44336' // 红色
      default: return '#409EFF' // 默认蓝色
    }
  }
  
  // 清除所有标记
  const clearMarkers = () => {
    markers.forEach(marker => marker.remove())
    markers = []
  }
  
  // 初始化地图
  const initMap = async () => {
    if (!mapContainer.value) return
    
    // 这里应该集成地图API，如高德地图、百度地图等
    // 以下为示例代码，实际实现需要根据使用的地图API调整
    
    // 尝试获取用户位置作为初始中心点
    let center = [116.4074, 39.9042] // 默认北京
    let zoom = 12
    
    try {
      // 检查URL参数中是否有位置信息
      if (route.query.lat && route.query.lng) {
        center = [parseFloat(route.query.lng), parseFloat(route.query.lat)]
        zoom = 15
        
        // 如果有名称参数，创建一个标记
        if (route.query.name) {
          setTimeout(() => {
            const marker = new mapboxgl.Marker({
              color: '#409EFF'
            })
              .setLngLat(center)
              .addTo(map)
            
            markers.push(marker)
            
            // 显示信息窗口
            selectedPlace.value = {
              name: route.query.name,
              location: {
                longitude: center[0],
                latitude: center[1]
              },
              address: '从地图导航而来',
              rating: 5.0,
              description: '该位置是通过地图导航功能直接定位而来。'
            }
          }, 1000)
        }
      } else {
        // 尝试获取用户当前位置
        const position = await getCurrentPosition()
        center = [position.longitude, position.latitude]
      }
    } catch (err) {
      console.error('Error getting initial position:', err)
    }
    
    // 创建地图实例
    setTimeout(() => {
      // 这里是地图初始化的模拟代码
      // 实际项目中应该使用真实的地图API，如高德地图、百度地图等
      const mapElement = mapContainer.value
      mapElement.innerHTML = `
        <div class="map-placeholder">
          <h3>地图加载中...</h3>
          <p>中心点: ${center[1]}, ${center[0]}</p>
          <p>缩放级别: ${zoom}</p>
          <p class="map-note">注意：这是一个地图模拟界面，实际项目中应集成真实地图API</p>
        </div>
      `
      
      // 模拟地图API
      map = {
        flyTo: (options) => {
          console.log('Map flyTo:', options)
          mapElement.querySelector('.map-placeholder').innerHTML = `
            <h3>地图已定位到</h3>
            <p>中心点: ${options.center[1]}, ${options.center[0]}</p>
            <p>缩放级别: ${options.zoom}</p>
            <p class="map-note">注意：这是一个地图模拟界面，实际项目中应集成真实地图API</p>
          `
        },
        resize: () => console.log('Map resize'),
        getZoom: () => zoom,
        zoomTo: (newZoom) => {
          zoom = newZoom
          console.log('Map zoom to:', newZoom)
        },
        setMapType: (type) => console.log('Map type changed to:', type),
        showTraffic: () => console.log('Traffic layer shown'),
        hideTraffic: () => console.log('Traffic layer hidden'),
        showPOI: () => console.log('POI layer shown'),
        hidePOI: () => console.log('POI layer hidden'),
        getBounds: () => ({
          getSouthWest: () => ({ lng: center[0] - 0.1, lat: center[1] - 0.1 }),
          getNorthEast: () => ({ lng: center[0] + 0.1, lat: center[1] + 0.1 })
        }),
        fitBounds: (bounds, options) => console.log('Map fit bounds:', bounds, options)
      }
      
      // 加载景点数据
      loadPlaces()
    }, 500)
  }
  
  // 监听路由参数变化
  watch(() => route.query, (newQuery) => {
    if (newQuery.lat && newQuery.lng && map) {
      map.flyTo({
        center: [parseFloat(newQuery.lng), parseFloat(newQuery.lat)],
        zoom: 15,
        essential: true
      })
    }
  }, { deep: true })
  
  // 组件挂载时初始化地图
  onMounted(() => {
    initMap()
    
    // 从URL参数中获取路线规划参数
    if (route.query.start) {
      routeStart.value = route.query.start
    }
    
    if (route.query.end) {
      routeEnd.value = route.query.end
      activeTab.value = 'route'
    }
  })
  
  // 组件卸载时清理资源
  onUnmounted(() => {
    clearMarkers()
    clearRoute()
    map = null
  })
  </script>
  
  <style scoped>
  .map-view-container {
    position: relative;
    width: 100%;
    height: calc(100vh - 60px); /* 减去header的高度 */
    overflow: hidden;
  }
  
  .map-container {
    width: 100%;
    height: 100%;
    background-color: #f5f7fa;
  }
  
  .map-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    color: #606266;
    background-color: #f5f7fa;
    padding: 20px;
  }
  
  .map-note {
    margin-top: 20px;
    color: #909399;
    font-size: 14px;
    font-style: italic;
  }
  
  .sidebar {
    position: absolute;
    top: 0;
    left: 0;
    width: 350px;
    height: 100%;
    background-color: white;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
    z-index: 10;
    transition: transform 0.3s ease;
  }
  
  .sidebar-collapsed {
    transform: translateX(-350px);
  }
  
  .sidebar-toggle {
    position: absolute;
    top: 50%;
    right: -30px;
    width: 30px;
    height: 60px;
    background-color: white;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    border-radius: 0 4px 4px 0;
    z-index: 11;
  }
  
  .sidebar-content {
    height: 100%;
    overflow-y: auto;
    padding: 20px;
  }
  
  .search-panel,
  .route-panel,
  .layers-panel {
    padding-bottom: 20px;
  }
  
  .search-history {
    margin-top: 15px;
  }
  
  .search-history-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }
  
  .search-history-header h4 {
    margin: 0;
    font-size: 14px;
    color: #606266;
  }
  
  .search-history-list {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
  }
  
  .search-results {
    margin-top: 20px;
  }
  
  .search-results h4 {
    margin: 0 0 10px;
    font-size: 14px;
    color: #606266;
  }
  
  .search-result-item {
    display: flex;
    padding: 10px;
    border-bottom: 1px solid #ebeef5;
    cursor: pointer;
  }
  
  .search-result-item:hover {
    background-color: #f5f7fa;
  }
  
  .result-icon {
    margin-right: 10px;
    color: #409EFF;
  }
  
  .result-info h5 {
    margin: 0 0 5px;
    font-size: 14px;
    color: #303133;
  }
  
  .result-info p {
    margin: 0;
    font-size: 12px;
    color: #909399;
  }
  
  .route-inputs {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 15px;
  }
  
  .waypoint-item {
    display: flex;
    align-items: center;
    gap: 5px;
  }
  
  .add-waypoint {
    margin: 5px 0;
  }
  
  .route-options {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }
  
  .route-summary {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
  }
  
  .route-info {
    display: flex;
    gap: 15px;
  }
  
  .route-distance,
  .route-duration {
    display: flex;
    align-items: center;
    color: #606266;
  }
  
  .route-distance i,
  .route-duration i {
    margin-right: 5px;
    color: #409EFF;
  }
  
  .layers-panel h4 {
    margin: 15px 0 10px;
    font-size: 14px;
    color: #606266;
  }
  
  .map-controls {
    position: absolute;
    bottom: 20px;
    right: 20px;
    z-index: 5;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  
  .place-info-card {
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    bottom: 20px;
    width: 90%;
    max-width: 600px;
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    z-index: 5;
    transition: bottom 0.3s ease;
  }
  
  .place-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px;
    border-bottom: 1px solid #ebeef5;
  }
  
  .place-card-header h3 {
    margin: 0;
    font-size: 16px;
    color: #303133;
  }
  
  .place-card-content {
    display: flex;
    padding: 15px;
  }
  
  .place-card-image {
    width: 120px;
    height: 90px;
    margin-right: 15px;
    flex-shrink: 0;
  }
  
  .place-card-image .el-image {
    width: 100%;
    height: 100%;
    border-radius: 4px;
  }
  
  .place-card-info {
    flex: 1;
  }
  
  .place-card-rating {
    display: flex;
    align-items: center;
    margin-bottom: 5px;
  }
  
  .place-card-rating span {
    margin-left: 5px;
    color: #ff9900;
    font-size: 14px;
  }
  
  .place-card-address {
    display: flex;
    align-items: flex-start;
    margin: 5px 0;
    color: #606266;
    font-size: 13px;
  }
  
  .place-card-address i {
    margin-right: 5px;
    margin-top: 3px;
    color: #409EFF;
  }
  
  .place-card-description {
    margin: 5px 0 0;
    color: #606266;
    font-size: 13px;
    line-height: 1.4;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
  }
  
  .place-card-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    padding: 10px 15px 15px;
  }
  
  .user-location-marker {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background-color: #ff4500;
    border: 2px solid white;
    box-shadow: 0 0 0 2px rgba(255, 69, 0, 0.4);
    position: relative;
  }
  
  .pulse {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background-color: rgba(255, 69, 0, 0.4);
    animation: pulse 1.5s infinite;
  }
  
  @keyframes pulse {
    0% {
      transform: translate(-50%, -50%) scale(0.5);
      opacity: 1;
    }
    100% {
      transform: translate(-50%, -50%) scale(1.5);
      opacity: 0;
    }
  }
  
  @media (max-width: 768px) {
    .sidebar {
      width: 280px;
    }
    
    .sidebar-collapsed {
      transform: translateX(-280px);
    }
    
    .place-info-card {
      width: 95%;
    }
    
    .place-card-image {
      width: 80px;
      height: 60px;
    }
  }
  </style>