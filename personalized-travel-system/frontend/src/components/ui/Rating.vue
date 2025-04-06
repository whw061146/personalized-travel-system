<template>
  <div class="custom-rating" :class="{ 'is-disabled': disabled }">
    <div v-if="label" class="rating-label">{{ label }}</div>
    <div class="rating-content">
      <div class="rating-items">
        <span
          v-for="(item, index) in max"
          :key="index"
          class="rating-item"
          :class="{
            'is-active': modelValue >= index + 1,
            'is-half-active': modelValue > index && modelValue < index + 1
          }"
          @mousemove="!disabled && !readonly && setHoverValue(index + 1, $event)"
          @mouseleave="!disabled && !readonly && clearHoverValue()"
          @click="!disabled && !readonly && setValue(index + 1)"
        >
          <i :class="[iconClasses(index + 1)]"></i>
        </span>
      </div>
      <div v-if="showText" class="rating-text">
        {{ currentText }}
      </div>
      <div v-if="showScore" class="rating-score">
        {{ modelValue }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Number,
    default: 0
  },
  max: {
    type: Number,
    default: 5
  },
  disabled: {
    type: Boolean,
    default: false
  },
  readonly: {
    type: Boolean,
    default: false
  },
  allowHalf: {
    type: Boolean,
    default: false
  },
  showText: {
    type: Boolean,
    default: false
  },
  showScore: {
    type: Boolean,
    default: false
  },
  texts: {
    type: Array,
    default: () => ['极差', '失望', '一般', '满意', '惊喜']
  },
  label: {
    type: String,
    default: ''
  },
  voidIcon: {
    type: String,
    default: 'el-icon-star-off'
  },
  activeIcon: {
    type: String,
    default: 'el-icon-star-on'
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const hoverValue = ref(0)

const currentText = computed(() => {
  const value = props.modelValue
  if (value === 0) {
    return '未评分'
  }
  // 根据评分获取对应的文本描述
  const index = Math.ceil(value) - 1
  return props.texts[index] || ''
})

const iconClasses = (index) => {
  const value = hoverValue.value || props.modelValue
  if (value >= index) {
    return props.activeIcon
  } else if (props.allowHalf && value + 0.5 >= index) {
    return props.activeIcon + ' is-half'
  } else {
    return props.voidIcon
  }
}

const setHoverValue = (value, event) => {
  if (props.allowHalf) {
    // 检测鼠标位置，如果在星星的左半部分，则设置为半星
    const target = event.target
    const rect = target.getBoundingClientRect()
    const halfWidth = rect.width / 2
    const offsetX = event.clientX - rect.left
    hoverValue.value = offsetX <= halfWidth ? value - 0.5 : value
  } else {
    hoverValue.value = value
  }
}

const clearHoverValue = () => {
  hoverValue.value = 0
}

const setValue = (value) => {
  let finalValue = value
  
  // 如果允许半星且鼠标在星星的左半部分
  if (props.allowHalf && hoverValue.value !== value) {
    finalValue = hoverValue.value
  }
  
  // 如果点击的是当前值，则清除评分
  if (finalValue === props.modelValue) {
    finalValue = 0
  }
  
  emit('update:modelValue', finalValue)
  emit('change', finalValue)
}
</script>

<style scoped>
.custom-rating {
  display: inline-flex;
  flex-direction: column;
  font-size: 14px;
  line-height: 1;
}

.rating-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.rating-content {
  display: flex;
  align-items: center;
}

.rating-items {
  display: inline-flex;
  margin-right: 10px;
}

.rating-item {
  margin-right: 6px;
  cursor: pointer;
  position: relative;
  font-size: 18px;
  color: #c0c4cc;
  transition: color 0.3s;
}

.rating-item:last-child {
  margin-right: 0;
}

.rating-item.is-active {
  color: #f7ba2a;
}

.rating-item.is-half-active {
  position: relative;
}

.rating-item.is-half-active:after {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 50%;
  height: 100%;
  overflow: hidden;
  color: #f7ba2a;
}

.rating-text {
  font-size: 14px;
  color: #909399;
  margin-left: 10px;
}

.rating-score {
  font-size: 16px;
  color: #f7ba2a;
  font-weight: bold;
  margin-left: 10px;
}

.is-disabled .rating-item {
  cursor: not-allowed;
}

.is-disabled .rating-text,
.is-disabled .rating-score {
  color: #c0c4cc;
}
</style>