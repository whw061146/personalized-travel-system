# 个性化旅游推荐系统 - 实现指南

## 项目开发流程 & 技术栈

本指南详细介绍如何按照 **后端 → 数据库 → 爬虫 → AI → 前端 → 部署** 的顺序开发 **个性化旅游推荐系统**。

---

## 1. 搭建后端框架（Flask）
**`backend/`**

> **目标**：搭建 Flask 应用，连接数据库，注册 API 路由。

### 开发步骤

#### 1.1 创建基础应用结构
1. **创建 `app.py`**（Flask 主入口）：
```python
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from routes import register_blueprints
from models import db
import config

app = Flask(__name__)

# 加载配置
app.config.from_object(config.Config)

# 初始化扩展
db.init_app(app)
CORS(app)
jwt = JWTManager(app)

# 注册所有蓝图
register_blueprints(app)

@app.route('/api/health')
def health_check():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

2. **创建 `config.py`**（配置数据库、JWT 密钥）：
```python
import os
from datetime import timedelta

class Config:
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@localhost/travel_system'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # 上传文件配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB 最大上传限制
```

3. **编写 `requirements.txt`**（安装所需依赖）：
```
Flask==2.0.1
Flask-SQLAlchemy==2.5.1
Flask-JWT-Extended==4.3.1
Flask-CORS==3.0.10
PyMySQL==1.0.2
Werkzeug==2.0.1
passlib==1.7.4
requests==2.26.0
numpy==1.21.2
pandas==1.3.3
scikit-learn==1.0
gensim==4.1.2
tensorflow==2.6.0
pillow==8.3.2
```

#### 1.2 设计数据库模型

4. **初始化 `schema.sql`**（创建 MySQL 表结构）：
```sql
CREATE DATABASE IF NOT EXISTS travel_system;
USE travel_system;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    preferences JSON,  -- 存储用户偏好的JSON数据
    avatar_url VARCHAR(255)
);

-- 景点表
CREATE TABLE IF NOT EXISTS places (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    location_lat DECIMAL(10, 8) NOT NULL,
    location_lng DECIMAL(11, 8) NOT NULL,
    category VARCHAR(50),  -- 景点类别（自然景观、历史遗迹等）
    images JSON,  -- 存储图片URL的JSON数组
    rating DECIMAL(2, 1),  -- 评分（1-5分）
    visit_time INT,  -- 建议游览时间（分钟）
    tags JSON,  -- 标签JSON数组（如"适合拍照"、"人少清静
