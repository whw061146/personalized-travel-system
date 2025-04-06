<template>
  <el-card class="recommend-card" :body-style="{ padding: '0' }">
    <div class="card-image" v-if="item.image">
      <img :src="item.image" :alt="item.title">
      <div class="card-tags" v-if="item.tags && item.tags.length">
        <el-tag v-for="tag in item.tags.slice(0, 2)" :key="tag" size="small" class="tag">{{ tag }}</el-tag>
        <span v-if="item.tags.length > 2" class="more-tags">+{{ item.tags.length - 2 }}</span>
      </div>
    </div>
    
    <div class="card-content">
      <div class="card-header">
        <h3 class="card-title">{{ item.title }}</h3>
        <div class="card-rating">
          <el-rate
            v-model="item.rating"
            disabled
            text-color="#ff9900"
            score-template="{value}"
          ></el-rate>
          <span class="rating-value">{{ item.rating.toFixed(1) }}</span>
        </div>
      </div>
      
      <p class="card-description">{{ truncateDescription(item.description) }}</p>
      
      <div class="card-meta">
        <span v-if="item.location" class="location">
          <i class="el-icon-location-outline"></i> {{ item.location }}
        </span>
        <span v-if="item.price" class="price">
          <i class="el-icon-price-tag"></i> {{ formatPrice(item.price) }}
        </span>
      </div>
      
      <div class="card-actions">
        <el-button type="primary" size="small" @click="viewDetails">查看详情</el-button>
        <el-button 
          size="small" 
          :type="item.isFavorite ? 'danger' : 'default'" 
          @click="toggleFavorite"
        >
          <i :class="item.isFavorite ? 'el-icon-star-on' : 'el-icon-star-off'"></i>
          {{ item.isFavorite ? '已收藏' : '收藏' }}
        </el-button>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

// 组件属性
const props = defineProps({
  item: {
    type: Object,
    required: true,
    default: () => ({
      id: '',
      title: '',
      description: '',
      image: '',
      rating: 0,
      location: '',
      price: null,
      tags: [],
      isFavorite: false
    })
  },
  maxDescriptionLength: {
    type: Number,
    default: 100
  }
})

// 组件事件
const emit = defineEmits(['view-details', 'toggle-favorite'])

// 截断描述文本
const truncateDescription = (text) => {
  if (!text) return ''
  return text.length > props.maxDescriptionLength
    ? text.substring(0, props.maxDescriptionLength) + '...'
    : text
}

// 格式化价格
const formatPrice = (price) => {
  if (!price && price !== 0) return '免费'
  return `¥${price}`
}

// 查看详情
const viewDetails = () => {
  emit('view-details', props.item)
}

// 切换收藏状态
const toggleFavorite = () => {
  emit('toggle-favorite', props.item)
}
</script>

<style scoped>
.recommend-card {
  width: 100%;
  margin-bottom: 20px;
  transition: transform 0.3s, box-shadow 0.3s;
  overflow: hidden;
}

.recommend-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.card-image {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s;
}

.recommend-card:hover .card-image img {
  transform: scale(1.05);
}

.card-tags {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 5px;
}

.tag {
  background-color: rgba(64, 158, 255, 0.8);
  color: white;
  border: none;
}

.more-tags {
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 10px;
}

.card-content {
  padding: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.card-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.card-rating {
  display: flex;
  align-items: center;
}

.rating-value {
  margin-left: 5px;
  font-weight: bold;
  color: #ff9900;
}

.card-description {
  margin: 10px 0;
  font-size: 14px;
  color: var(--text-regular);
  line-height: 1.5;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  font-size: 13px;
  color: var(--text-secondary);
}

.location, .price {
  display: flex;
  align-items: center;
  gap: 5px;
}

.card-actions {
  display: flex;
  justify-content: space-between;
}
</style>