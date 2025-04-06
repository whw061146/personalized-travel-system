<template>
  <button
    class="custom-button"
    :class="[
      type ? `button-${type}` : '',
      size ? `button-${size}` : '',
      { 'is-disabled': disabled, 'is-loading': loading, 'is-round': round, 'is-circle': circle }
    ]"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <i v-if="loading" class="el-icon-loading"></i>
    <i v-if="icon && !loading" :class="icon"></i>
    <span v-if="$slots.default && !circle" class="button-text">
      <slot></slot>
    </span>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'default',
    validator: (value) => {
      return ['default', 'primary', 'success', 'warning', 'danger', 'info', 'text'].includes(value)
    }
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => {
      return ['large', 'medium', 'small', 'mini'].includes(value)
    }
  },
  icon: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  round: {
    type: Boolean,
    default: false
  },
  circle: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click'])

const handleClick = (event) => {
  if (props.disabled || props.loading) return
  emit('click', event)
}
</script>

<style scoped>
.custom-button {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  line-height: 1;
  height: 36px;
  white-space: nowrap;
  cursor: pointer;
  background: #fff;
  border: 1px solid #dcdfe6;
  color: #606266;
  text-align: center;
  box-sizing: border-box;
  outline: none;
  margin: 0;
  transition: .1s;
  font-weight: 500;
  padding: 0 20px;
  font-size: 14px;
  border-radius: 4px;
}

.custom-button:hover {
  color: #409eff;
  border-color: #c6e2ff;
  background-color: #ecf5ff;
}

.custom-button:active {
  color: #3a8ee6;
  border-color: #3a8ee6;
  outline: none;
}

.button-primary {
  color: #fff;
  background-color: #409eff;
  border-color: #409eff;
}

.button-primary:hover {
  background: #66b1ff;
  border-color: #66b1ff;
  color: #fff;
}

.button-primary:active {
  background: #3a8ee6;
  border-color: #3a8ee6;
  color: #fff;
}

.button-success {
  color: #fff;
  background-color: #67c23a;
  border-color: #67c23a;
}

.button-success:hover {
  background: #85ce61;
  border-color: #85ce61;
  color: #fff;
}

.button-success:active {
  background: #5daf34;
  border-color: #5daf34;
  color: #fff;
}

.button-warning {
  color: #fff;
  background-color: #e6a23c;
  border-color: #e6a23c;
}

.button-warning:hover {
  background: #ebb563;
  border-color: #ebb563;
  color: #fff;
}

.button-warning:active {
  background: #cf9236;
  border-color: #cf9236;
  color: #fff;
}

.button-danger {
  color: #fff;
  background-color: #f56c6c;
  border-color: #f56c6c;
}

.button-danger:hover {
  background: #f78989;
  border-color: #f78989;
  color: #fff;
}

.button-danger:active {
  background: #dd6161;
  border-color: #dd6161;
  color: #fff;
}

.button-info {
  color: #fff;
  background-color: #909399;
  border-color: #909399;
}

.button-info:hover {
  background: #a6a9ad;
  border-color: #a6a9ad;
  color: #fff;
}

.button-info:active {
  background: #82848a;
  border-color: #82848a;
  color: #fff;
}

.button-text {
  border-color: transparent;
  color: #409eff;
  background: transparent;
  padding-left: 0;
  padding-right: 0;
}

.button-text:hover {
  color: #66b1ff;
  border-color: transparent;
  background-color: transparent;
}

.button-text:active {
  color: #3a8ee6;
  background-color: transparent;
}

.button-large {
  height: 40px;
  padding: 0 20px;
  font-size: 14px;
}

.button-small {
  height: 32px;
  padding: 0 15px;
  font-size: 12px;
}

.button-mini {
  height: 28px;
  padding: 0 15px;
  font-size: 12px;
}

.is-round {
  border-radius: 20px;
}

.is-circle {
  border-radius: 50%;
  padding: 0;
  width: 36px;
}

.button-large.is-circle {
  width: 40px;
}

.button-small.is-circle {
  width: 32px;
}

.button-mini.is-circle {
  width: 28px;
}

.is-disabled {
  color: #c0c4cc;
  cursor: not-allowed;
  background-image: none;
  background-color: #fff;
  border-color: #ebeef5;
}

.button-primary.is-disabled,
.button-success.is-disabled,
.button-warning.is-disabled,
.button-danger.is-disabled,
.button-info.is-disabled {
  color: #fff;
  background-color: #a0cfff;
  border-color: #a0cfff;
}

.button-text.is-disabled {
  background-color: transparent;
}

.is-loading {
  position: relative;
  pointer-events: none;
}

.is-loading:before {
  pointer-events: none;
  content: '';
  position: absolute;
  left: -1px;
  top: -1px;
  right: -1px;
  bottom: -1px;
  border-radius: inherit;
  background-color: rgba(255,255,255,.35);
}

.button-text {
  margin-left: 5px;
}
</style>