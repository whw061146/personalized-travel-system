# `routes/` API 模块说明

## 目录结构
```
routes/
│── __init__.py        # Blueprint 统一注册
│── auth.py           # 用户认证 API
│── recommend.py      # 推荐系统 API
│── search.py         # 搜索功能 API
│── map.py            # 路径规划 API
│── diary.py          # 旅游日记 API
│── food.py           # 美食 API
│── indoor.py         # 室内导航 API
│── aigc.py           # AI 生成内容 API
```

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
- **功能**：用户注册、登录、获取用户信息。
- **实现方式**：
  - 使用 `Flask-JWT-Extended` 进行身份验证。
  - `bcrypt` 进行密码哈希加密。
  - 用户数据存储在 MySQL 数据库。
- **如何执行**：
  ```bash
  # 注册用户
  curl -X POST http://127.0.0.1:5000/auth/register -H "Content-Type: application/json" -d '{"username": "test", "email": "test@example.com", "password": "123456"}'
  
  # 登录用户
  curl -X POST http://127.0.0.1:5000/auth/login -H "Content-Type: application/json" -d '{"email": "test@example.com", "password": "123456"}'
  
  # 获取用户信息（需要 JWT Token）
  curl -X GET http://127.0.0.1:5000/auth/me -H "Authorization: Bearer <JWT_TOKEN>"
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

---

✅ **完整执行指南已更新！**
📌 **包含 Flask 服务器启动命令、如何测试 API**
📌 **提供了 `curl` 命令示例，方便测试**
🚀 **你现在可以运行 `python app.py` 启动服务器，开始测试 API！告诉我下一步！** 🎯
