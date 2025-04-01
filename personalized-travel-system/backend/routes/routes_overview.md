# 后端路由模块概览

本文档提供了`backend/routes`文件夹中所有路由文件的详细说明，帮助开发者快速了解API结构和功能。

## 文件结构

```
backend/routes/
├── __init__.py       # 蓝图注册模块
├── aigc.py           # AI生成内容API
├── auth.py           # 用户认证API
├── diary.py          # 旅游日记API
├── food.py           # 美食相关API
├── indoor.py         # 室内导航API
├── map.py            # 地图和路径规划API
├── recommend.py      # 推荐系统API
├── search.py         # 搜索功能API
└── routes_documentation.md  # API使用文档
```

## 各文件功能说明

### `__init__.py`

**主要功能**：注册所有蓝图到Flask应用

- 导入所有路由模块中定义的蓝图
- 提供`register_blueprints`函数，将所有蓝图注册到Flask应用
- 为每个蓝图设置适当的URL前缀

### `auth.py`

**主要功能**：用户认证和账户管理

- 用户注册API (`/register`)
  - 验证用户名、邮箱和密码
  - 创建新用户并保存到数据库
  
- 用户登录API (`/login`)
  - 验证用户凭据
  - 生成JWT访问令牌和刷新令牌
  
- 用户登出API (`/logout`)
  - 使当前JWT令牌失效
  
- 获取用户信息API (`/me`)
  - 返回当前登录用户的详细信息
  
- 更新用户信息API (`/update`)
  - 允许用户更新个人资料
  
- 修改密码API (`/change-password`)
  - 验证当前密码并更新为新密码
  
- 刷新令牌API (`/refresh-token`)
  - 使用刷新令牌生成新的访问令牌

### `recommend.py`

**主要功能**：提供个性化推荐服务

- 景点推荐API (`/places`)
  - 基于用户偏好推荐景点
  - 返回评分最高的景点
  
- 基于历史的推荐API (`/places/history`)
  - 分析用户历史浏览和收藏记录
  - 推荐相似景点
  
- 附近景点推荐API (`/places/nearby`)
  - 基于用户当前位置推荐附近景点
  - 支持设置搜索半径
  
- AI推荐API (`/places/ai`)
  - 使用AI算法进行个性化推荐

### `search.py`

**主要功能**：提供全文搜索和筛选功能

- 全文搜索API (`/all`)
  - 搜索景点和美食信息
  - 支持多种筛选条件和排序方式
  
- 景点搜索API (`/places`)
  - 按类型、位置、评分等筛选景点
  - 支持关键词搜索和标签筛选
  
- 美食搜索API (`/foods`)
  - 按菜系、价格、评分等筛选美食
  - 支持关键词搜索和位置筛选
  
- 旅游日记搜索API (`/diaries`)
  - 搜索公开的旅游日记
  - 支持按地点、标签等筛选

### `map.py`

**主要功能**：提供地图数据和路径规划

- 地图数据API (`/data`)
  - 获取指定区域的地图数据
  - 包括景点、餐厅等POI信息
  
- 路径规划API (`/route`)
  - 计算两点之间的最佳路径
  - 支持多种交通方式
  
- 多点路径规划API (`/multi-route`)
  - 解决旅行商问题(TSP)
  - 优化多个景点的游览顺序
  
- 附近设施查询API (`/nearby-facilities`)
  - 查询附近的厕所、ATM等设施

### `diary.py`

**主要功能**：旅游日记的创建和管理

- 获取公开日记API (`/`)
  - 返回公开的旅游日记列表
  - 支持分页和排序
  
- 获取用户日记API (`/my`)
  - 返回当前用户的所有日记
  - 包括私密和公开日记
  
- 创建日记API (`/create`)
  - 创建新的旅游日记
  - 支持上传图片
  
- 获取日记详情API (`/<diary_id>`)
  - 返回指定日记的详细信息
  
- 更新日记API (`/<diary_id>`)
  - 更新现有日记内容
  
- 删除日记API (`/<diary_id>`)
  - 删除指定的日记
  
- 上传图片API (`/upload-image`)
  - 上传日记相关图片
  - 返回图片URL

### `food.py`

**主要功能**：美食推荐和信息查询

- 美食推荐API (`/recommend`)
  - 基于用户偏好和位置推荐美食
  - 支持设置搜索半径
  
- 获取美食详情API (`/<food_id>`)
  - 返回指定美食的详细信息
  
- 获取餐厅信息API (`/restaurant/<restaurant_id>`)
  - 返回指定餐厅的详细信息
  
- 美食评价API (`/<food_id>/rate`)
  - 允许用户对美食进行评分
  - 更新美食的平均评分

### `indoor.py`

**主要功能**：提供室内导航服务

- 室内地图API (`/map`)
  - 获取指定建筑物的室内地图数据
  - 支持按楼层查询
  
- 室内路径规划API (`/route`)
  - 计算室内两点之间的最佳路径
  - 支持多楼层路径规划
  
- 室内设施查询API (`/facilities`)
  - 查询室内的厕所、电梯等设施位置
  
- 室内位置搜索API (`/search`)
  - 搜索室内特定位置
  - 支持关键词搜索

### `aigc.py`

**主要功能**：AI生成内容服务

- 生成图像API (`/generate-image`)
  - 使用Stable Diffusion生成旅游图像
  - 支持设置风格和尺寸
  
- 生成文本API (`/generate-text`)
  - 使用大型语言模型生成旅游相关文本
  - 支持多种文本类型
  
- 图像风格转换API (`/style-transfer`)
  - 将用户上传的图片转换为特定艺术风格
  - 支持多种艺术风格
  
- 生成旅游计划API (`/generate-plan`)
  - 基于用户偏好生成个性化旅游计划
  - 包括行程安排和推荐景点

## API通用规范

1. **认证方式**：大部分API需要JWT认证，在请求头中添加`Authorization: Bearer <token>`

2. **响应格式**：所有API返回JSON格式，包含以下字段：
   - `status`: 请求状态，`success`或`error`
   - `data`: 响应数据（成功时）
   - `message`: 响应消息（错误时）

3. **错误处理**：使用标准HTTP状态码表示错误，常见状态码：
   - 200: 请求成功
   - 201: 资源创建成功
   - 400: 请求参数错误
   - 401: 未授权
   - 404: 资源不存在
   - 500: 服务器内部错误

4. **分页**：支持分页的API接受以下查询参数：
   - `page`: 页码，默认为1
   - `per_page`: 每页项目数，默认为10

5. **排序**：支持排序的API接受以下查询参数：
   - `sort_by`: 排序字段
   - `sort_order`: 排序方式，`asc`或`desc`