<template>
  <div class="custom-card" :class="{ 'is-hoverable': hoverable }">
    <div v-if="$slots.header || title" class="card-header">
      <slot name="header">
        <div class="card-title">{{ title }}</div>
      </slot>
    </div>
    <div class="card-body" :style="bodyStyle">
      <slot></slot>
    </div>
    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  bodyStyle: {
    type: Object,
    default: () => ({})
  },
  hoverable: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.custom-card {
  border-radius: 4px;
  border: 1px solid #ebeef5;
  background-color: #fff;
  overflow: hidden;
  color: #303133;
  transition: 0.3s;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.is-hoverable:hover {
  box-shadow: 0 6px 16px 0 rgba(0, 0, 0, 0.2);
  transform: translateY(-5px);
}

.card-header {
  padding: 18px 20px;
  border-bottom: 1px solid #ebeef5;
  box-sizing: border-box;
}

.card-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin: 0;
}

.card-body {
  padding: 20px;
}

.card-footer {
  padding: 10px 20px;
  border-top: 1px solid #ebeef5;
}
</style>