# `routes/` API 模块说明

## 目录
- [`routes/` API 模块说明](#routes-api-模块说明)
  - [目录](#目录)
  - [**如何运行整个后端 API 服务器**](#如何运行整个后端-api-服务器)
    - [**1️⃣ 确保 Conda 虚拟环境激活**](#1️⃣-确保-conda-虚拟环境激活)
    - [**2️⃣ 进入 `backend/` 目录**](#2️⃣-进入-backend-目录)
    - [**3️⃣ 安装依赖（如果尚未安装）**](#3️⃣-安装依赖如果尚未安装)
    - [**4️⃣ 运行 Flask 服务器**](#4️⃣-运行-flask-服务器)
    - [**5️⃣ 测试 API 是否正常运行**](#5️⃣-测试-api-是否正常运行)
  - [**API 详情**](#api-详情)
  - [**1️⃣ `auth.py`（用户认证 API）**](#1️⃣-authpy用户认证-api)
  - [**2️⃣ `recommend.py`（推荐系统 API）**](#2️⃣-recommendpy推荐系统-api)
  - [**3️⃣ `search.py`（搜索功能 API）**](#3️⃣-searchpy搜索功能-api)
  - [**4️⃣ `map.py`（路径规划 API）**](#4️⃣-mappy路径规划-api)
  - [**5️⃣ `aigc.py`（AI 生成内容 API）**](#5️⃣-aigcpyai-生成内容-api)
  - [**6️⃣ `diary.py`（旅游日记 API）**](#6️⃣-diarypy旅游日记-api)

## **如何运行整个后端 API 服务器**
### **1️⃣ 确保 Conda 虚拟环境激活**
```bash
conda activate travel-env
```

### **2️⃣ 进入 `backend/` 目录**
```bash
cd backend
```

### **3️⃣ 安装依赖（如果尚未安装）**
```bash
pip install -r requirements.txt
```

### **4️⃣ 运行 Flask 服务器**
```bash
python app.py
```
如果需要使用 `gunicorn` 进行生产环境运行，可以执行：
```bash
gunicorn --bind 0.0.0.0:5000 wsgi:app
```

### **5️⃣ 测试 API 是否正常运行**
在浏览器或 Postman 访问：
```
http://127.0.0.1:5000/
```
如果后端正常运行，会返回 `Flask is running!`。

## **API 详情**

## **1️⃣ `auth.py`（用户认证 API）**
- **功能**：用户注册、登录、获取用户信息、更新用户信息、修改密码、注销账户、刷新令牌。
- **实现方式**：
  - 使用 `Flask-JWT-Extended` 进行身份验证。
  - `werkzeug.security` 进行密码哈希加密。
  - 用户数据存储在 MySQL 数据库。
  - 密码强度和邮箱格式验证。
- **如何执行**：
  ```bash
  # 注册用户
  curl -X POST http://127.0.0.1:5000/auth/register -H "Content-Type: application/json" -d '{"username": "test", "email": "test@example.com", "password": "Password123", "avatar_url": "http://example.com/avatar.jpg"}'
  
  # 登录用户
  curl -X POST http://127.0.0.1:5000/auth/login -H "Content-Type: application/json" -d '{"email": "test@example.com", "password": "Password123"}'
  
  # 获取用户信息（需要 JWT Token）
  curl -X GET http://127.0.0.1:5000/auth/me -H "Authorization: Bearer <JWT_TOKEN>"
  
  # 更新用户信息（需要 JWT Token）
  curl -X PUT http://127.0.0.1:5000/auth/update -H "Content-Type: application/json" -H "Authorization: Bearer <JWT_TOKEN>" -d '{"username": "new_username", "avatar_url": "http://example.com/new_avatar.jpg", "preferences": {"theme": "dark"}}'
  
  # 修改密码（需要 JWT Token）
  curl -X PUT http://127.0.0.1:5000/auth/change-password -H "Content-Type: application/json" -H "Authorization: Bearer <JWT_TOKEN>" -d '{"current_password": "Password123", "new_password": "NewPassword456"}'
  
  # 注销账户（需要 JWT Token）
  curl -X DELETE http://127.0.0.1:5000/auth/delete-account -H "Content-Type: application/json" -H "Authorization: Bearer <JWT_TOKEN>" -d '{"password": "Password123"}'
  
  # 刷新令牌（需要 JWT Token）
  curl -X POST http://127.0.0.1:5000/auth/refresh-token -H "Authorization: Bearer <JWT_TOKEN>"
  ```

## **2️⃣ `recommend.py`（推荐系统 API）**
- **功能**：基于评分和用户行为，推荐景点、美食、游记。
- **实现方式**：
  - 通过 `SQLAlchemy` 查询 MySQL 数据库。
  - 根据评分降序排序，返回 Top-K 推荐项。
- **如何执行**：
  ```bash
  curl -X GET http://127.0.0.1:5000/recommend/places  # 推荐景点
  curl -X GET http://127.0.0.1:5000/recommend/foods   # 推荐美食
  curl -X GET http://127.0.0.1:5000/recommend/diaries # 推荐游记
  ```

## **3️⃣ `search.py`（搜索功能 API）**
- **功能**：支持搜索景点、美食、旅游日记。
- **实现方式**：
  - 采用 SQL `ilike` 进行模糊匹配。
  - 查询 MySQL 数据库，并返回相关搜索结果。
- **如何执行**：
  ```bash
  curl -X GET "http://127.0.0.1:5000/search/places?q=北京"
  curl -X GET "http://127.0.0.1:5000/search/foods?q=川菜"
  curl -X GET "http://127.0.0.1:5000/search/diaries?q=长城"
  ```

## **4️⃣ `map.py`（路径规划 API）**
- **功能**：计算最短路径、多目标优化路径。
- **实现方式**：
  - 采用 `networkx` 计算 Dijkstra 最短路径。
  - 解决旅行商问题（TSP）优化旅行线路。
- **如何执行**：
  ```bash
  curl -X GET "http://127.0.0.1:5000/map/shortest-path?start_id=1&end_id=2"
  curl -X POST "http://127.0.0.1:5000/map/tsp-route" -H "Content-Type: application/json" -d '{"places": [1,2,3,4]}'
  ```

## **5️⃣ `aigc.py`（AI 生成内容 API）**
- **功能**：使用 AI 生成旅游日记或图片。
- **实现方式**：
  - 采用 `OpenAI GPT-4` 生成文本。
  - `Stable Diffusion` 生成旅游图片。
- **如何执行**：
  ```bash
  curl -X POST "http://127.0.0.1:5000/aigc/generate-diary" -H "Content-Type: application/json" -d '{"user_id": 1, "prompt": "长城游记"}'
  curl -X POST "http://127.0.0.1:5000/aigc/generate-image" -H "Content-Type: application/json" -d '{"user_id": 1, "prompt": "故宫日落"}'
  ```

## **6️⃣ `diary.py`（旅游日记 API）**
- **功能**：创建、查看、评分旅游日记。
- **实现方式**：
  - 使用`SQLAlchemy`操作MySQL数据库。
  - 支持文本内容和图片/视频URL。
- **如何执行**：
  ```bash
  # 创建旅游日记
  curl -X POST "http://127.0.0.1:5000/diary/create" -H "Content-Type: application/json" -H "Authorization: Bearer <JWT_TOKEN>" -d '{"title": "北京游记", "content": "今天游览了长城...", "image_url": "http://example.com/image.jpg"}'
  
  # 获取所有旅游日记
  curl -X GET "http://127.0.0.1:5000/diary/all"
  
  # 获取单个旅游日记详情
  curl -X GET "http://127.0.0.1:5000/diary/1"
  
  # 评分旅游日记
  curl -X POST "http://127.0.0.1:5000/diary/rate/1" -H "Content-Type: application/json" -H "Authorization: Bearer <JWT_TOKEN>" -d '{"rating": 5}'

## **API 通用说明**

### 认证要求
- 需要认证的API会标注`@jwt_required()`
- 认证方式：在请求头中添加`Authorization: Bearer <JWT_TOKEN>`
- JWT Token通过`/auth/login`接口获取

### 错误处理
所有API遵循以下错误状态码约定：
- 200: 请求成功
- 201: 资源创建成功
- 400: 请求参数错误
- 401: 未授权（缺少Token或Token无效）
- 404: 资源不存在
- 409: 资源冲突（如用户已存在）
- 500: 服务器内部错误

### 跨域支持
所有API支持跨域请求(CORS)，前端可以直接调用。

### API版本
当前API版本：v1.0.0
更新日期：2023-XX-XX

### Windows PowerShell用户注意事项
在Windows PowerShell中，请使用以下命令格式替代文档中的curl命令：

```powershell
# 方法1：使用curl.exe
curl.exe -X GET "http://127.0.0.1:5000/indoor/indoor-path?start_id=1&end_id=2"

# 方法2：使用Invoke-WebRequest
Invoke-WebRequest -Method GET -Uri "http://127.0.0.1:5000/indoor/indoor-path?start_id=1&end_id=2"

# 方法3：使用Invoke-RestMethod（推荐用于API调用）
Invoke-RestMethod -Method GET -Uri "http://127.0.0.1:5000/indoor/indoor-path?start_id=1&end_id=2"
```
