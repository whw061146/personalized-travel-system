<template>
    <div class="diary-container">
      <!-- 页面头部 -->
      <div class="diary-header">
        <div class="container">
          <h1>旅行日记</h1>
          <p>记录您的旅行点滴，分享精彩瞬间</p>
        </div>
      </div>
      
      <!-- 主要内容区域 -->
      <div class="container diary-content">
        <!-- 顶部操作栏 -->
        <div class="diary-actions">
          <el-button type="primary" icon="el-icon-plus" @click="$router.push('/diary/create')">创建日记</el-button>
          <div class="diary-filters">
            <el-input
              v-model="searchQuery"
              placeholder="搜索日记"
              prefix-icon="el-icon-search"
              clearable
              @keyup.enter="handleSearch"
            />
            <el-select v-model="sortBy" placeholder="排序方式" @change="handleSortChange">
              <el-option label="最新发布" value="newest" />
              <el-option label="最早发布" value="oldest" />
              <el-option label="点赞最多" value="most_liked" />
            </el-select>
            <el-select v-model="privacyFilter" placeholder="隐私设置" @change="handlePrivacyChange">
              <el-option label="全部" value="all" />
              <el-option label="公开" value="public" />
              <el-option label="仅自己可见" value="private" />
            </el-select>
          </div>
        </div>
        
        <!-- 日记列表 -->
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="5" animated />
        </div>
        
        <el-empty v-else-if="diaries.length === 0" description="暂无日记">
          <el-button type="primary" @click="$router.push('/diary/create')">立即创建</el-button>
        </el-empty>
        
        <div v-else class="diary-list">
          <el-card v-for="diary in diaries" :key="diary.id" class="diary-card" shadow="hover">
            <div class="diary-card-header">
              <div class="diary-user-info">
                <el-avatar :size="40" :src="diary.userAvatar">{{ diary.userName.charAt(0) }}</el-avatar>
                <div>
                  <h3>{{ diary.userName }}</h3>
                  <p class="diary-date">{{ formatDate(diary.createdAt) }}</p>
                </div>
              </div>
              <div class="diary-privacy">
                <el-tag size="small" :type="diary.isPrivate ? 'info' : 'success'">
                  {{ diary.isPrivate ? '仅自己可见' : '公开' }}
                </el-tag>
              </div>
            </div>
            
            <div class="diary-title" @click="viewDiaryDetail(diary.id)">
              <h2>{{ diary.title }}</h2>
            </div>
            
            <div class="diary-content-preview" @click="viewDiaryDetail(diary.id)">
              <p>{{ diary.content }}</p>
            </div>
            
            <div class="diary-images" v-if="diary.images && diary.images.length > 0" @click="viewDiaryDetail(diary.id)">
              <el-image 
                v-for="(img, index) in diary.images.slice(0, 3)" 
                :key="index"
                :src="img"
                fit="cover"
                class="diary-image"
              />
              <div class="more-images" v-if="diary.images.length > 3">
                <span>+{{ diary.images.length - 3 }}</span>
              </div>
            </div>
            
            <div class="diary-locations" v-if="diary.locations && diary.locations.length > 0">
              <div class="location-tag" v-for="(location, index) in diary.locations" :key="index">
                <i class="el-icon-location"></i>
                <span>{{ location.name }}</span>
              </div>
            </div>
            
            <div class="diary-footer">
              <div class="diary-stats">
                <div class="stat-item">
                  <i class="el-icon-view"></i>
                  <span>{{ diary.viewCount || 0 }}</span>
                </div>
                <div class="stat-item">
                  <i class="el-icon-chat-dot-round"></i>
                  <span>{{ diary.commentCount || 0 }}</span>
                </div>
                <div 
                  class="stat-item" 
                  :class="{ 'active': diary.isLiked }"
                  @click="toggleLike(diary)"
                >
                  <i :class="diary.isLiked ? 'el-icon-star-on' : 'el-icon-star-off'"></i>
                  <span>{{ diary.likeCount || 0 }}</span>
                </div>
              </div>
              <div class="diary-actions">
                <el-dropdown v-if="diary.isOwner" trigger="click" @command="handleCommand($event, diary.id)">
                  <el-button type="text" icon="el-icon-more"></el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="edit">编辑</el-dropdown-item>
                      <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </el-card>
        </div>
        
        <!-- 分页 -->
        <div class="pagination-container" v-if="totalItems > 0">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[5, 10, 20, 50]"
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
  import { ref, reactive, computed, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import { useUserStore } from '../store'
  
  // 路由实例
  const router = useRouter()
  
  // 用户状态管理
  const userStore = useUserStore()
  
  // 页面状态
  const loading = ref(false)
  const diaries = ref([])
  const totalItems = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(10)
  const searchQuery = ref('')
  const sortBy = ref('newest')
  const privacyFilter = ref('all')
  
  // 获取日记列表
  const fetchDiaries = async () => {
    if (!userStore.isLoggedIn) {
      ElMessage.warning('请先登录')
      router.push('/login')
      return
    }
    
    loading.value = true
    
    try {
      // 构建查询参数
      const params = new URLSearchParams()
      params.append('page', currentPage.value)
      params.append('size', pageSize.value)
      params.append('sort', sortBy.value)
      
      if (searchQuery.value) {
        params.append('q', searchQuery.value)
      }
      
      if (privacyFilter.value !== 'all') {
        params.append('privacy', privacyFilter.value)
      }
      
      // 调用API获取日记列表
      const response = await fetch(`/api/diaries?${params.toString()}`, {
        headers: {
          'Authorization': `Bearer ${userStore.token}`
        }
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch diaries')
      }
      
      const data = await response.json()
      diaries.value = data.items
      totalItems.value = data.total
    } catch (err) {
      console.error('Error fetching diaries:', err)
      ElMessage.error('获取日记列表失败，请稍后再试')
      diaries.value = []
      totalItems.value = 0
    } finally {
      loading.value = false
    }
  }
  
  // 处理搜索
  const handleSearch = () => {
    currentPage.value = 1
    fetchDiaries()
  }
  
  // 处理排序变化
  const handleSortChange = () => {
    currentPage.value = 1
    fetchDiaries()
  }
  
  // 处理隐私设置变化
  const handlePrivacyChange = () => {
    currentPage.value = 1
    fetchDiaries()
  }
  
  // 处理分页大小变化
  const handleSizeChange = (size) => {
    pageSize.value = size
    fetchDiaries()
  }
  
  // 处理页码变化
  const handleCurrentChange = (page) => {
    currentPage.value = page
    fetchDiaries()
  }
  
  // 查看日记详情
  const viewDiaryDetail = (id) => {
    router.push(`/diary/${id}`)
  }
  
  // 切换点赞状态
  const toggleLike = async (diary) => {
    if (!userStore.isLoggedIn) {
      ElMessage.warning('请先登录')
      router.push('/login')
      return
    }
    
    try {
      const method = diary.isLiked ? 'DELETE' : 'POST'
      const response = await fetch(`/api/diaries/${diary.id}/like`, {
        method,
        headers: {
          'Authorization': `Bearer ${userStore.token}`
        }
      })
      
      if (response.ok) {
        diary.isLiked = !diary.isLiked
        diary.likeCount = diary.isLiked ? (diary.likeCount + 1) : (diary.likeCount - 1)
        ElMessage.success(diary.isLiked ? '已点赞' : '已取消点赞')
      } else {
        throw new Error('操作失败')
      }
    } catch (err) {
      console.error('Error toggling like:', err)
      ElMessage.error('操作失败，请稍后再试')
    }
  }
  
  // 处理下拉菜单命令
  const handleCommand = (command, diaryId) => {
    if (command === 'edit') {
      router.push(`/diary/edit/${diaryId}`)
    } else if (command === 'delete') {
      confirmDelete(diaryId)
    }
  }
  
  // 确认删除
  const confirmDelete = (diaryId) => {
    ElMessageBox.confirm(
      '确定要删除这篇日记吗？此操作不可逆。',
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(() => {
      deleteDiary(diaryId)
    }).catch(() => {
      // 用户取消删除
    })
  }
  
  // 删除日记
  const deleteDiary = async (diaryId) => {
    try {
      const response = await fetch(`/api/diaries/${diaryId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${userStore.token}`
        }
      })
      
      if (response.ok) {
        ElMessage.success('日记已删除')
        // 从列表中移除已删除的日记
        diaries.value = diaries.value.filter(diary => diary.id !== diaryId)
        // 更新总数
        totalItems.value -= 1
      } else {
        throw new Error('删除失败')
      }
    } catch (err) {
      console.error('Error deleting diary:', err)
      ElMessage.error('删除失败，请稍后再试')
    }
  }
  
  // 格式化日期
  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
  }
  
  // 组件挂载时获取数据
  onMounted(() => {
    fetchDiaries()
  })
  </script>
  
  <style scoped>
  .diary-container {
    padding-bottom: 40px;
  }
  
  .diary-header {
    background-color: #409EFF;
    color: white;
    padding: 40px 0;
    margin-bottom: 30px;
    text-align: center;
  }
  
  .diary-header h1 {
    font-size: 2rem;
    margin-bottom: 10px;
  }
  
  .diary-header p {
    font-size: 1.1rem;
    opacity: 0.9;
  }
  
  .diary-content {
    max-width: 1000px;
    margin: 0 auto;
  }
  
  .diary-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    flex-wrap: wrap;
    gap: 10px;
  }
  
  .diary-filters {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
  }
  
  .loading-container {
    padding: 20px 0;
  }
  
  .diary-list {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }
  
  .diary-card {
    cursor: pointer;
    transition: transform 0.2s;
  }
  
  .diary-card:hover {
    transform: translateY(-3px);
  }
  
  .diary-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
  }
  
  .diary-user-info {
    display: flex;
    align-items: center;
  }
  
  .diary-user-info div {
    margin-left: 10px;
  }
  
  .diary-user-info h3 {
    margin: 0;
    font-size: 16px;
    color: #303133;
  }
  
  .diary-date {
    margin: 5px 0 0;
    font-size: 12px;
    color: #909399;
  }
  
  .diary-title h2 {
    margin: 0 0 15px;
    font-size: 18px;
    color: #303133;
  }
  
  .diary-content-preview {
    margin-bottom: 15px;
    color: #606266;
    line-height: 1.6;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
  }
  
  .diary-images {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
    position: relative;
  }
  
  .diary-image {
    width: calc((100% - 20px) / 3);
    height: 150px;
    border-radius: 4px;
  }
  
  .more-images {
    position: absolute;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    color: white;
    padding: 5px 10px;
    border-radius: 0 0 4px 0;
    font-size: 14px;
  }
  
  .diary-locations {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 15px;
  }
  
  .location-tag {
    display: flex;
    align-items: center;
    background-color: #f5f7fa;
    padding: 5px 10px;
    border-radius: 4px;
    font-size: 13px;
    color: #606266;
  }
  
  .location-tag i {
    margin-right: 5px;
    color: #409EFF;
  }
  
  .diary-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid #ebeef5;
    padding-top: 15px;
  }
  
  .diary-stats {
    display: flex;
    gap: 15px;
  }
  
  .stat-item {
    display: flex;
    align-items: center;
    color: #909399;
    cursor: pointer;
  }
  
  .stat-item i {
    margin-right: 5px;
  }
  
  .stat-item.active {
    color: #409EFF;
  }
  
  .pagination-container {
    margin-top: 30px;
    display: flex;
    justify-content: center;
  }
  
  @media (max-width: 768px) {
    .diary-header {
      padding: 30px 0;
    }
    
    .diary-header h1 {
      font-size: 1.5rem;
    }
    
    .diary-header p {
      font-size: 1rem;
    }
    
    .diary-actions {
      flex-direction: column;
      align-items: flex-start;
    }
    
    .diary-filters {
      width: 100%;
      margin-top: 10px;
    }
    
    .diary-image {
      height: 100px;
    }
  }
  </style>