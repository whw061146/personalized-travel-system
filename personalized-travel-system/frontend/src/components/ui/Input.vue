<template>
  <div class="custom-input" :class="{ 'is-disabled': disabled }">
    <div v-if="label" class="input-label">{{ label }}</div>
    <div class="input-wrapper">
      <div v-if="prefixIcon" class="input-prefix">
        <i :class="prefixIcon"></i>
      </div>
      <input
        ref="inputRef"
        class="input-inner"
        :class="{ 'has-prefix': prefixIcon, 'has-suffix': suffixIcon || clearable }"
        :type="showPassword ? 'text' : type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :maxlength="maxlength"
        @input="handleInput"
        @focus="handleFocus"
        @blur="handleBlur"
        @change="handleChange"
      />
      <div v-if="clearable && modelValue" class="input-suffix input-clear" @click="clearInput">
        <i class="el-icon-circle-close"></i>
      </div>
      <div v-else-if="suffixIcon || type === 'password'" class="input-suffix">
        <i 
          v-if="type === 'password'"
          :class="[showPassword ? 'el-icon-view' : 'el-icon-hide']"
          @click="togglePasswordVisibility"
        ></i>
        <i v-else :class="suffixIcon"></i>
      </div>
    </div>
    <div v-if="error" class="input-error">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  type: {
    type: String,
    default: 'text'
  },
  label: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: '请输入'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  readonly: {
    type: Boolean,
    default: false
  },
  clearable: {
    type: Boolean,
    default: false
  },
  prefixIcon: {
    type: String,
    default: ''
  },
  suffixIcon: {
    type: String,
    default: ''
  },
  maxlength: {
    type: Number,
    default: undefined
  },
  error: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'input', 'change', 'focus', 'blur', 'clear'])

const inputRef = ref(null)
const showPassword = ref(false)

const handleInput = (event) => {
  const value = event.target.value
  emit('update:modelValue', value)
  emit('input', value)
}

const handleChange = (event) => {
  emit('change', event.target.value)
}

const handleFocus = (event) => {
  emit('focus', event)
}

const handleBlur = (event) => {
  emit('blur', event)
}

const clearInput = () => {
  emit('update:modelValue', '')
  emit('clear')
  // 聚焦回输入框
  inputRef.value?.focus()
}

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}

// 方法：聚焦输入框
const focus = () => {
  inputRef.value?.focus()
}

// 方法：失焦输入框
const blur = () => {
  inputRef.value?.blur()
}

// 暴露方法给父组件
defineExpose({
  focus,
  blur,
  inputRef
})
</script>

<style scoped>
.custom-input {
  position: relative;
  font-size: 14px;
  width: 100%;
  margin-bottom: 15px;
}

.input-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.input-wrapper {
  position: relative;
  display: flex;
  width: 100%;
}

.input-inner {
  -webkit-appearance: none;
  background-color: #fff;
  background-image: none;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  box-sizing: border-box;
  color: #606266;
  display: inline-block;
  font-size: inherit;
  height: 36px;
  line-height: 36px;
  outline: none;
  padding: 0 15px;
  transition: border-color .2s cubic-bezier(.645,.045,.355,1);
  width: 100%;
}

.input-inner:focus {
  outline: none;
  border-color: #409eff;
}

.input-inner::placeholder {
  color: #c0c4cc;
}

.input-inner.has-prefix {
  padding-left: 35px;
}

.input-inner.has-suffix {
  padding-right: 35px;
}

.input-prefix,
.input-suffix {
  position: absolute;
  height: 100%;
  top: 0;
  display: flex;
  align-items: center;
  color: #c0c4cc;
  font-size: 14px;
}

.input-prefix {
  left: 10px;
}

.input-suffix {
  right: 10px;
}

.input-clear {
  cursor: pointer;
}

.input-clear:hover {
  color: #909399;
}

.input-error {
  color: #f56c6c;
  font-size: 12px;
  margin-top: 5px;
}

.is-disabled .input-inner {
  background-color: #f5f7fa;
  border-color: #e4e7ed;
  color: #c0c4cc;
  cursor: not-allowed;
}

.is-disabled .input-prefix,
.is-disabled .input-suffix {
  cursor: not-allowed;
}
</style>