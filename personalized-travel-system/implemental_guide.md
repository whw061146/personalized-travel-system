# **? 个性化旅游推荐系统 - 开发指南**

## **? 项目开发顺序 & 任务分解**

本指南详细描述如何按照 **后端 → 数据库 → 爬虫 → AI → 前端 → 部署** 的顺序开发 **个性化旅游推荐系统**。

---

## **? 1. 配置后端框架（Flask）**
**? `backend/`**

> **目标**：搭建 Flask 主应用，配置数据库，注册 API 蓝图。

? **步骤**
1. **创建 `app.py`**（Flask 主入口）
   - 初始化 Flask
   - 连接 MySQL 数据库
   - 注册 API 蓝图
   - 启动服务器

2. **配置 `config.py`**（配置数据库、JWT 密钥）
   - MySQL 连接参数
   - JWT 认证密钥

3. **编写 `requirements.txt`**（安装所需依赖）
   - `Flask`、`SQLAlchemy`、`Flask-JWT-Extended`、`Flask-CORS`

4. **初始化 `schema.sql`**（定义 MySQL 表结构）

5. **编写 `wsgi.py`**（生产环境 WSGI 入口）

6. **创建 `routes/` 目录，编写 API 模块**
   - `routes/auth.py`（用户认证 API）
   - `routes/recommend.py`（推荐系统 API）
   - `routes/search.py`（搜索功能 API）
   - `routes/map.py`（路径规划 API）
   - `routes/diary.py`（旅游日记 API）
   - `routes/food.py`（美食 API）
   - `routes/indoor.py`（室内导航 API）
   - `routes/aigc.py`（AI 生成内容 API）

---

## **? 2. 设计数据库（MySQL + SQLAlchemy）**
**? `backend/models/`**

> **目标**：设计数据库表结构，支持所有核心功能。

? **步骤**
1. **创建 `models/__init__.py`**（数据库初始化）
2. **创建 `models/user.py`**（用户模型）
3. **创建 `models/place.py`**（景点模型）
4. **创建 `models/food.py`**（美食模型）
5. **创建 `models/diary.py`**（旅游日记模型）
6. **创建 `models/path.py`**（路径规划数据结构）
7. **运行 `database/init_db.py`**（创建数据库表 & 插入测试数据）

---

## **? 3. 爬取地图 & 美食数据**
**? `crawler/`**

> **目标**：获取 **真实的校园 & 景点地图数据**，以及 **美食数据**。

? **步骤**
1. **编写 `crawler/scrape_osm.py`**（爬取 OpenStreetMap 地图数据）
2. **编写 `crawler/scrape_places.py`**（爬取景点 & 学校数据）
3. **编写 `crawler/scrape_food.py`**（爬取美食数据）
4. **存储数据到 `crawler/data/`**
5. **解析数据并存入 MySQL**

---

## **? 4. 实现 AI 推荐系统**
**? `ai_recommendation/`**

> **目标**：使用 AI 实现个性化推荐 & 旅游动画生成。

? **步骤**
1. **编写 `content_based.py`**（基于内容的推荐）
2. **编写 `collaborative_filter.py`**（协同过滤推荐）
3. **编写 `vector_search.py`**（向量数据库 + 近似最近邻搜索）
4. **编写 `generate_animation.py`**（Stable Diffusion 生成旅游动画）

---

## **? 5. 搭建前端（Vue.js / React）**
**? `frontend/`**

> **目标**：开发前端界面，连接后端 API，实现地图可视化。

? **步骤**
1. **创建 `package.json`**（定义 Vue.js / React 依赖）
2. **配置 `vite.config.js`**（跨域代理）
3. **创建 `src/main.js`**（前端入口）
4. **创建 `src/router.js`**（Vue Router 配置）
5. **创建 `src/store.js`**（Vuex / Pinia 状态管理）
6. **创建 `views/` 页面组件**
7. **创建 `components/` 组件库**

---

## **? 6. 编写测试 & 文档**
**? `docs/`**

> **目标**：撰写 API 文档、安装指南 & 开发者手册。

? **步骤**
1. **创建 `README.md`**（项目介绍）
2. **创建 `API_Documentation.md`**（API 说明文档）
3. **创建 `setup_guide.md`**（安装 & 部署指南）
4. **创建 `development_guide.md`**（开发 & 贡献指南）

---

## **? 7. 运行 & 部署**
**? `scripts/`**

> **目标**：启动项目，部署到服务器。

? **步骤**
1. **创建 `scripts/start_dev.sh`**（启动 Flask & Vue.js 开发环境）
2. **创建 `scripts/deploy.sh`**（自动部署脚本）
3. **创建 `scripts/backup_db.sh`**（数据库备份脚本）

---

## **? 8. 运行项目**

```bash
# 安装后端依赖
cd backend
pip install -r requirements.txt

# 初始化数据库
python database/init_db.py

# 运行 Flask 服务器
python backend/app.py

# 安装前端依赖
cd frontend
npm install

# 运行前端
npm run dev

# 启动爬虫
python crawler/scrape_osm.py

# 运行 AI 推荐
python ai_recommendation/content_based.py
```

---

## **? 总结**
? **后端**（Flask API）
? **数据库**（MySQL）
? **爬取真实数据**（OpenStreetMap / 高德 API）
? **AI 推荐系统**（Word2Vec / BERT / Stable Diffusion）
? **前端开发**（Vue.js / React）
? **部署测试**

? **至此，你的个性化旅游推荐系统已准备就绪！** ?
