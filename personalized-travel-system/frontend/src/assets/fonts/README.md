# 字体文件目录

此目录用于存放网站使用的字体文件。

## 使用说明

1. 将字体文件(.woff, .woff2, .ttf等格式)放置在此目录中
2. 在CSS中通过@font-face规则引入字体

## 字体列表

目前项目使用的字体包括：

- 系统默认字体：'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif
- 代码字体：'Source Code Pro', monospace

## 字体引入示例

```css
@font-face {
  font-family: 'CustomFont';
  src: url('../fonts/CustomFont.woff2') format('woff2'),
       url('../fonts/CustomFont.woff') format('woff');
  font-weight: normal;
  font-style: normal;
  font-display: swap;
}
```