# 个性化旅游推荐系统

一个基于Flask、Vue.js、MySQL和AI推荐算法的个性化旅游推荐系统，为用户提供定制化的旅游体验。

## 项目简介

个性化旅游推荐系统是一个综合性的旅游服务平台，通过AI算法分析用户偏好，为用户提供个性化的景点、美食和路线推荐。系统还集成了地图导航、旅游日记、室内导航等功能，并利用AIGC技术生成旅游相关内容，提升用户体验。

## 功能特点

- **个性化推荐**：基于用户偏好和行为数据，推荐最适合的景点和美食
- **智能路径规划**：根据用户选择的景点，规划最优游览路线
- **旅游日记**：记录和分享旅游体验
- **美食推荐**：推荐当地特色美食和餐厅
- **室内导航**：提供大型场所（如博物馆、商场）的室内导航
- **AI生成内容**：使用Stable Diffusion生成旅游相关的图像和动画
- **地图集成**：整合地图服务，提供位置和设施查询

## 技术架构

### 后端
- **框架**：Flas
- **数据库**：MySQL
- **认证**：JWT (JSON Web Token)
- **API**：RESTful API

### 前端
- **框架**：Vue.js
- **构建工具**：Vite
- **状态管理**：Vuex/Pinia
- **路由**：Vue Router

### AI推荐系统
- **基于内容的推荐**：使用Word2Vec/BERT
- **协同过滤**：基于用户行为分析
- **向量搜索**：ANN (近似最近邻搜索)
- **AIGC**：Stable Diffusion生成旅游动画

### 数据采集
- 使用爬虫从OpenStreetMap获取地图数据
- 通过高德/百度API获取美食和景点数据

## 项目结构

```
personalized_travel_system/
│── backend/                   # 后端（Flask API）
│── frontend/                  # 前端（Vue.js）
│── database/                  # 数据管理
│── crawler/                   # 爬虫（获取地图和美食数据）
│── ai_recommendation/         # AI推荐系统
│── docs/                      # 文档
│── scripts/                   # 启动和维护脚本
```

详细的项目结构请参考 [structure.md](./structure.md) 文件。

## 安装指南

### 环境要求
- Python 3.8+
- Node.js 14+
- MySQL 8.0+

### 后端安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/personalized-travel-system.git
cd personalized-travel-system/backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python ../database/init_db.py
```

### 前端安装

```bash
cd ../frontend
npm install
```

## 使用说明

### 启动开发环境

```bash
# 启动后端服务
cd backend
python app.py

# 启动前端服务（新终端）
cd frontend
npm run dev
```

或使用提供的脚本：

```bash
# Linux/Mac
./scripts/start_dev.sh

# Windows
.\scripts\start_dev.bat
```

访问 http://localhost:3000 即可使用系统。

## 开发指南

开发流程遵循 **后端 → 数据库 → 爬虫 → AI → 前端 → 部署** 的顺序。详细的开发指南请参考 [implemental_guide.md](./implemental_guide.md) 和 [development_guide.md](./docs/development_guide.md)。

## API文档

API文档请参考 [API_Documentation.md](./docs/API_Documentation.md)。

## 贡献指南

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](./LICENSE) 文件。
