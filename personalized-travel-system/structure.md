# 项目结构

```plaintext
personalized_travel_system/
│── backend/                   # 后端（Flask API）
│   │── app.py                 # Flask 主应用入口
│   │── config.py              # 配置文件（数据库、密钥等）
│   │── requirements.txt       # Python 依赖清单
│   │── schema.sql             # MySQL 数据库表结构
│   │── static/                # 静态资源（如上传图片）
│   │── routes/                # 后端 API 逻辑（Flask Blueprint）
│   │   │── __init__.py        # Blueprint 初始化
│   │   │── auth.py            # 用户登录、注册
│   │   │── recommend.py       # 景点/美食/游记推荐
│   │   │── search.py          # 搜索功能
│   │   │── map.py             # 地图相关 API（路径规划、设施查询）
│   │   │── diary.py           # 旅游日记 API
│   │   │── food.py            # 美食 API
│   │   │── indoor.py          # 室内导航 API
│   │   │── aigc.py            # AI 生成内容 API（Stable Diffusion）
│   │── models/                # 数据库模型（SQLAlchemy ORM）
│   │   │── __init__.py        # 连接数据库
│   │   │── user.py            # 用户模型
│   │   │── place.py           # 景点模型
│   │   │── food.py            # 美食模型
│   │   │── diary.py           # 旅游日记模型
│   │   │── path.py            # 路径规划数据结构
│   │── utils/                 # 工具函数
│   │   │── helpers.py         # 辅助工具函数（计算距离、格式转换等）
│   │   │── security.py        # 加密 & 鉴权
│   │── tests/                 # 单元测试
│   │── wsgi.py                # 生产环境 WSGI 入口（Gunicorn）
│
│── frontend/                  # 前端（Vue.js / React）
│   │── public/                # 静态资源
│   │── src/                   # 主要前端代码
│   │   │── assets/            # 图片、CSS
│   │   │── components/        # Vue 组件
│   │   │── views/             # 页面组件（首页、搜索、推荐、地图等）
│   │   │── router.js          # Vue Router 路由配置
│   │   │── store.js           # Vuex/Pinia 状态管理
│   │   │── main.js            # Vue 入口
│   │── package.json           # 前端依赖清单
│   │── vite.config.js         # Vite 配置（如跨域代理）
│
│── database/                  # 数据管理（数据初始化 & 脚本）
│   │── init_db.py             # 初始化数据库（建表 & 插入示例数据）
│   │── migrate.py             # 数据库迁移（如添加字段）
│   │── seed_data.sql          # 预置数据（用户、景点、美食等）
│
│── crawler/                   # 爬虫（获取真实地图 & 美食数据）
│   │── scrape_osm.py          # 通过 OpenStreetMap 获取道路 & 设施数据
│   │── scrape_food.py         # 获取美食数据（高德 API / 百度 API）
│   │── scrape_places.py       # 爬取景点 & 校园信息
│   │── data/                  # 存储爬取的 JSON / CSV 数据
│
│── ai_recommendation/         # AI 推荐（个性化推荐 & AIGC）
│   │── content_based.py       # 基于内容推荐（Word2Vec / BERT）
│   │── collaborative_filter.py# 协同过滤推荐（用户行为分析）
│   │── vector_search.py       # 向量数据库 ANN 近似最近邻搜索
│   │── generate_animation.py  # 生成旅游动画（Stable Diffusion）
│
│── docs/                      # 文档
│   │── API_Documentation.md   # API 说明文档（Swagger/Postman 参考）
│   │── README.md              # 项目介绍 & 运行指南
│   │── setup_guide.md         # 安装 & 部署指南
│   │── development_guide.md   # 开发 & 贡献指南
│
│── scripts/                   # 启动 & 维护脚本
│   │── start_dev.sh           # 启动开发环境（前后端 & 数据库）
│   │── deploy.sh              # 部署到服务器的脚本
│   │── backup_db.sh           # 备份数据库
│
│── .gitignore                 # Git 忽略文件（排除 venv、node_modules 等）
│── docker-compose.yml         # Docker Compose 配置（若需要容器化）
│── LICENSE                    # 许可证（可选）
```

