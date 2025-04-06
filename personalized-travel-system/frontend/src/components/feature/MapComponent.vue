<template>
  <div class="map-component">
    <div class="map-container" ref="mapContainer"></div>
    
    <div class="map-controls" v-if="showControls">
      <div class="search-box">
        <el-input
          v-model="searchQuery"
          placeholder="搜索地点"
          clearable
          @keyup.enter="searchPlaces"
        >
          <template #append>
            <el-button @click="searchPlaces">
              <i class="el-icon-search"></i>
            </el-button>
          </template>
        </el-input>
      </div>
      
      <div class="filter-controls">
        <el-select v-model="selectedCategory" placeholder="类别" clearable @change="filterPlaces">
          <el-option
            v-for="category in categories"
            :key="category.value"
            :label="category.label"
            :value="category.value"
          ></el-option>
        </el-select>
        
        <el-select v-model="selectedRating" placeholder="评分" clearable @change="filterPlaces">
          <el-option label="4星以上" :value="4"></el-option>
          <el-option label="3星以上" :value="3"></el-option>
          <el-option label="2星以上" :value="2"></el-option>
        </el-select>
      </div>
    </div>
    
    <div class="place-info" v-if="selectedPlace">
      <div class="place-header">
        <h3>{{ selectedPlace.name }}</h3>
        <el-rate
          v-model="selectedPlace.rating"
          disabled
          text-color="#ff9900"
          score-template="{value}"
        ></el-rate>
      </div>
      
      <p class="place-address">
        <i class="el-icon-location-information"></i>
        {{ selectedPlace.address }}
      </p>
      
      <div class="place-details">
        <p v-if="selectedPlace.description">{{ selectedPlace.description }}</p>
        
        <div class="place-tags" v-if="selectedPlace.tags && selectedPlace.tags.length">
          <el-tag
            v-for="tag in selectedPlace.tags"
            :key="tag"
            size="small"
            class="mr-1 mb-1"
          >
            {{ tag }}
          </el-tag>
        </div>
      </div>
      
      <div class="place-actions">
        <el-button type="primary" size="small" @click="viewPlaceDetails">
          查看详情
        </el-button>
        <el-button size="small" @click="addToFavorites" v-if="isLoggedIn">
          <i class="el-icon-star-off"></i> 收藏
        </el-button>
        <el-button size="small" @click="getDirections">
          <i class="el-icon-position"></i> 导航
        </el-button>
      </div>
      
      <el-button class="close-info" @click="selectedPlace = null">
        <i class="el-icon-close"></i>
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../store'
import 'leaflet/dist/leaflet.css'

// 组件属性
const props = defineProps({
  initialCenter: {
    type: Array,
    default: () => [39.9042, 116.4074] // 默认北京中心
  },
  initialZoom: {
    type: Number,
    default: 12
  },
  places: {
    type: Array,
    default: () => []
  },
  showControls: {
    type: Boolean,
    default: true
  },
  height: {
    type: String,
    default: '500px'
  }
})

// 组件事件
const emit = defineEmits(['place-selected', 'place-added', 'search-completed'])

const router = useRouter()
const userStore = useUserStore()

// 地图相关引用和状态
const mapContainer = ref(null)
const map = ref(null)
const markers = ref([])
const selectedPlace = ref(null)

// 搜索和筛选状态
const searchQuery =