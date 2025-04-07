# 图片资源目录

此目录用于存放网站使用的图片资源。

## 使用说明

1. 将图片文件(.jpg, .png, .svg等格式)放置在此目录中
2. 在Vue组件中通过相对路径或导入方式引用图片

## 图片分类

为保持良好的组织结构，建议按以下分类存放图片：

- `backgrounds/`: 背景图片
- `banners/`: 横幅和广告图片
- `logos/`: 网站和合作伙伴logo
- `places/`: 景点图片
- `food/`: 美食图片
- `ui/`: UI相关图片元素

## 图片引入示例

```vue
<!-- 在Vue组件中使用 -->
<template>
  <img src="@/assets/images/logos/logo.png" alt="网站Logo">
</template>

<style>
.banner {
  background-image: url('@/assets/images/backgrounds/banner-bg.jpg');
}
</style>
```

## 注意事项

1. 图片应进行适当压缩，以提高加载速度
2. 考虑使用WebP等现代图片格式以提高性能
3. 为图片添加合适的alt属性以提高可访问性