<template>
  <div class="custom-select" :class="{ 'is-disabled': disabled }">
    <div v-if="label" class="select-label">{{ label }}</div>
    <div
      class="select-trigger"
      :class="{ 'is-focus': isDropdownVisible }"
      @click="toggleDropdown"
    >
      <div class="select-value" :class="{ 'is-placeholder': !selectedLabel }">
        <template v-if="multiple && selectedValues.length">
          <div class="select-tags">
            <div
              v-for="(item, index) in selectedOptions"
              :key="index"
              class="select-tag"
            >
              <span>{{ item.label }}</span>
              <i
                class="el-icon-close tag-close"
                @click.stop="removeTag(item.value)"
              ></i>
            </div>
          </div>
        </template>
        <template v-else>
          {{ selectedLabel || placeholder }}
        </template>
      </div>
      <div class="select-arrow">
        <i :class="['el-icon-arrow-down', { 'is-reverse': isDropdownVisible }]"></i>
      </div>
    </div>
    
    <transition name="select-dropdown">
      <div v-show="isDropdownVisible" class="select-dropdown">
        <div class="select-dropdown-list">
          <div
            v-for="(option, index) in options"
            :key="index"
            class="select-option"
            :class="{
              'is-selected': isOptionSelected(option.value),
              'is-disabled': option.disabled
            }"
            @click="selectOption(option)"
          >
            {{ option.label }}
          </div>
          <div v-if="options.length === 0" class="select-empty">
            无数据
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number, Array],
    default: ''
  },
  options: {
    type: Array,
    default: () => []
  },
  placeholder: {
    type: String,
    default: '请选择'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  multiple: {
    type: Boolean,
    default: false
  },
  label: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const isDropdownVisible = ref(false)

// 计算选中的值
const selectedValues = computed(() => {
  if (props.multiple) {
    return Array.isArray(props.modelValue) ? props.modelValue : []
  }
  return props.modelValue ? [props.modelValue] : []
})

// 计算选中的选项
const selectedOptions = computed(() => {
  return props.options.filter(option => selectedValues.value.includes(option.value))
})

// 计算显示的标签
const selectedLabel = computed(() => {
  if (props.multiple) {
    return selectedOptions.value.length > 0 
      ? selectedOptions.value.map(item => item.label).join(', ')
      : ''
  }
  
  const selected = selectedOptions.value[0]
  return selected ? selected.label : ''
})

// 判断选项是否被选中
const isOptionSelected = (value) => {
  return selectedValues.value.includes(value)
}

// 切换下拉菜单显示状态
const toggleDropdown = () => {
  if (props.disabled) return
  isDropdownVisible.value = !isDropdownVisible.value
}

// 选择选项
const selectOption = (option) => {
  if (props.disabled || option.disabled) return
  
  let newValue
  
  if (props.multiple) {
    newValue = [...selectedValues.value]
    const index = newValue.indexOf(option.value)
    
    if (index > -1) {
      newValue.splice(index, 1)
    } else {
      newValue.push(option.value)
    }
  } else {
    newValue = option.value
    isDropdownVisible.value = false
  }
  
  emit('update:modelValue', newValue)
  emit('change', newValue)
}

// 移除标签
const removeTag = (value) => {
  if (props.disabled) return
  
  const newValue = selectedValues.value.filter(v => v !== value)
  emit('update:modelValue', newValue)
  emit('change', newValue)
}

// 点击外部关闭下拉菜单
const handleClickOutside = (event) => {
  const target = event.target
  if (isDropdownVisible.value && !event.target.closest('.custom-select')) {
    isDropdownVisible.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.custom-select {
  position: relative;
  font-size: 14px;
  width: 100%;
  margin-bottom: 15px;
}

.select-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.select-trigger {
  position: relative;
  display: flex;
  align-items: center;
  background-color: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 0 30px 0 15px;
  height: 36px;
  line-height: 36px;
  cursor: pointer;
  transition: border-color 0.2s;
}

.select-trigger:hover {
  border-color: #c0c4cc;
}

.select-trigger.is-focus {
  border-color: #409eff;
}

.select-value {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #606266;
}

.is-placeholder {
  color: #c0c4cc;
}

.select-arrow {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #c0c4cc;
  font-size: 12px;
  transition: transform 0.3s;
}

.select-arrow .is-reverse {
  transform: rotate(180deg);
}

.select-dropdown {
  position: absolute;
  top: calc(100% + 5px);
  left: 0;
  width: 100%;
  max-height: 200px;
  background-color: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  z-index: 10;
  overflow: auto;
}

.select-dropdown-list {
  padding: 6px 0;
}

.select-option {
  padding: 0 15px;
  height: 34px;
  line-height: 34px;
  color: #606266;
  cursor: pointer;
}

.select-option:hover {
  background-color: #f5f7fa;
}

.select-option.is-selected {
  color: #409eff;
  font-weight: bold;
  background-color: #f5f7fa;
}

.select-option.is-disabled {
  color: #c0c4cc;
  cursor: not-allowed;
}

.select-empty {
  padding: 10px 15px;
  color: #909399;
  text-align: center;
}

.select-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.select-tag {
  display: flex;
  align-items: center;
  background-color: #f0f2f5;
  border-radius: 2px;
  padding: 0 5px;
  height: 22px;
  line-height: 22px;
  font-size: 12px;
  color: #606266;
}

.tag-close {
  margin-left: 4px;
  font-size: 12px;
  cursor: pointer;
}

.tag-close:hover {
  color: #409eff;
}

.is-disabled .select-trigger {
  background-color: #f5f7fa;
  border-color: #e4e7ed;
  color: #c0c4cc;
  cursor: not-allowed;
}

.select-dropdown-enter-active,
.select-dropdown-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.select-dropdown-enter-from,
.select-dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>