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
# Web框架和扩展
Flask==2.0.1
Flask-SQLAlchemy==2.5.1
Flask-JWT-Extended==4.3.1
Flask-CORS==3.0.10
Flask-RESTful==0.3.9
Flask-Migrate==3.1.0
Werkzeug==2.0.1
gunicorn==20.1.0

# 数据库连接
PyMySQL==1.0.2
SQLAlchemy==1.4.23

# 认证与安全
passlib==1.7.4
email-validator==1.1.3
pyjwt==2.1.0

# 网络请求与爬虫
requests==2.26.0
BeautifulSoup4==4.10.0
Selenium==4.0.0
lxml==4.6.3

# 数据处理与分析
numpy==1.21.2
pandas==1.3.3
matplotlib==3.4.3
seaborn==0.11.2

# 机器学习与AI
scikit-learn==1.0
gensim==4.1.2
tensorflow==2.6.0
keras==2.6.0
faiss-cpu==1.7.1

# 图像处理
pillow==8.3.2
opencv-python==4.5.3

# 工具库
python-dotenv==0.19.0
tqdm==4.62.2
joblib==1.0.1
pytz==2021.1
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
    tags JSON,  -- 标签JSON数组（如"适合拍照"、"人少清静"）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 美食表
CREATE TABLE IF NOT EXISTS foods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    location_lat DECIMAL(10, 8) NOT NULL,
    location_lng DECIMAL(11, 8) NOT NULL,
    category VARCHAR(50),  -- 美食类别（如川菜、粤菜等）
    images JSON,  -- 存储图片URL的JSON数组
    price_level TINYINT,  -- 价格等级（1-5）
    rating DECIMAL(2, 1),  -- 评分（1-5分）
    tags JSON,  -- 标签JSON数组（如"招牌菜"、"人气爆棚"）
    business_hours JSON,  -- 营业时间JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 旅游日记表
CREATE TABLE IF NOT EXISTS diaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    content TEXT,
    images JSON,  -- 存储图片URL的JSON数组
    location_lat DECIMAL(10, 8),
    location_lng DECIMAL(11, 8),
    visit_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 用户收藏表
CREATE TABLE IF NOT EXISTS favorites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    place_id INT,
    food_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE,
    FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE CASCADE
);

-- 用户评分表
CREATE TABLE IF NOT EXISTS ratings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    place_id INT,
    food_id INT,
    rating DECIMAL(2, 1) NOT NULL,  -- 评分（1-5分）
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE,
    FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE CASCADE
);

-- 路径规划表
CREATE TABLE IF NOT EXISTS paths (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100),
    places JSON,  -- 存储景点ID的JSON数组
    path_data JSON,  -- 存储路径数据的JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

5. **创建 SQLAlchemy ORM 模型**（`models/user.py`）：
```python
from . import db
from datetime import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    preferences = db.Column(db.JSON)
    avatar_url = db.Column(db.String(255))
    
    # 关系
    diaries = db.relationship('Diary', backref='author', lazy=True)
    favorites = db.relationship('Favorite', backref='user', lazy=True)
    ratings = db.relationship('Rating', backref='user', lazy=True)
    paths = db.relationship('Path', backref='user', lazy=True)
    
    def __init__(self, username, email, password, preferences=None, avatar_url=None):
        self.username = username
        self.email = email
        self.set_password(password)
        self.preferences = preferences or {}
        self.avatar_url = avatar_url
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'preferences': self.preferences,
            'avatar_url': self.avatar_url
        }
```

#### 1.3 实现 API 路由

6. **创建 Blueprint 初始化**（`routes/__init__.py`）：
```python
from flask import Blueprint

# 创建蓝图
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
recommend_bp = Blueprint('recommend', __name__, url_prefix='/api/recommend')
search_bp = Blueprint('search', __name__, url_prefix='/api/search')
map_bp = Blueprint('map', __name__, url_prefix='/api/map')
diary_bp = Blueprint('diary', __name__, url_prefix='/api/diary')
food_bp = Blueprint('food', __name__, url_prefix='/api/food')
indoor_bp = Blueprint('indoor', __name__, url_prefix='/api/indoor')
aigc_bp = Blueprint('aigc', __name__, url_prefix='/api/aigc')

# 导入路由处理函数
from . import auth, recommend, search, map, diary, food, indoor, aigc

def register_blueprints(app):
    """注册所有蓝图到应用"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(recommend_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(map_bp)
    app.register_blueprint(diary_bp)
    app.register_blueprint(food_bp)
    app.register_blueprint(indoor_bp)
    app.register_blueprint(aigc_bp)
```

7. **实现认证 API**（`routes/auth.py`）：
```python
from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from . import auth_bp
from models.user import User
from models import db

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # 验证必填字段
    if not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({'error': '缺少必填字段'}), 400
    
    # 检查用户名和邮箱是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '用户名已存在'}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': '邮箱已注册'}), 409
    
    # 创建新用户
    user = User(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        preferences=data.get('preferences'),
        avatar_url=data.get('avatar_url')
    )
    
    db.session.add(user)
    db.session.commit()
    
    # 生成访问令牌
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': '注册成功',
        'access_token': access_token,
        'user': user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # 验证必填字段
    if not all(k in data for k in ('username', 'password')):
        return jsonify({'error': '缺少必填字段'}), 400
    
    # 查找用户
    user = User.query.filter_by(username=data['username']).first()
    
    # 验证密码
    if not user or not user.check_password(data['password']):
        return jsonify({'error': '用户名或密码错误'}), 401
    
    # 生成访问令牌
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': '登录成功',
        'access_token': access_token,
        'user': user.to_dict()
    })

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    return jsonify(user.to_dict())

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    data = request.get_json()
    
    # 更新用户信息
    if 'username' in data and data['username'] != user.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': '用户名已存在'}), 409
        user.username = data['username']
    
    if 'email' in data and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': '邮箱已注册'}), 409
        user.email = data['email']
    
    if 'password' in data:
        user.set_password(data['password'])
    
    if 'preferences' in data:
        user.preferences = data['preferences']
    
    if 'avatar_url' in data:
        user.avatar_url = data['avatar_url']
    
    db.session.commit()
    
    return jsonify({
        'message': '个人信息更新成功',
        'user': user.to_dict()
    })
```

---

## 2. 数据库管理与初始化
**`database/`**

> **目标**：初始化数据库，创建表结构，插入示例数据。

### 开发步骤

#### 2.1 数据库初始化脚本

1. **创建 `init_db.py`**：
```python
import os
import sys
import pymysql
import json
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入配置
from backend.config import Config

def init_database():
    """初始化数据库和表结构"""
    # 解析数据库连接字符串
    db_uri = Config.SQLALCHEMY_DATABASE_URI
    db_info = db_uri.replace('mysql+pymysql://', '').split('@')[0].split(':')
    username = db_info[0]
    password = db_info[1].split('/')[0]
    host = db_uri.split('@')[1].split('/')[0]
    database = db_uri.split('/')[-1]
    
    # 连接 MySQL（不指定数据库）
    conn = pymysql.connect(
        host=host,
        user=username,
        password=password,
        charset='utf8mb4'
    )
    
    try:
        with conn.cursor() as cursor:
            # 创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute(f"USE {database}")
            
            # 读取并执行 schema.sql
            with open('backend/schema.sql', 'r', encoding='utf-8') as f:
                sql_commands = f.read()
                for command in sql_commands.split(';'):
                    if command.strip():
                        cursor.execute(command)
            
            conn.commit()
            print(f"数据库 {database} 和表结构创建成功")
    finally:
        conn.close()

def insert_sample_data():
    """插入示例数据"""
    # 连接到已创建的数据库
    db_uri = Config.SQLALCHEMY_DATABASE_URI
    db_info = db_uri.replace('mysql+pymysql://', '').split('@')[0].split(':')
    username = db_info[0]
    password = db_info[1].split('/')[0]
    host = db_uri.split('@')[1].split('/')[0]
    database = db_uri.split('/')[-1]
    
    conn = pymysql.connect(
        host=host,
        user=username,
        password=password,
        database=database,
        charset='utf8mb4'
    )
    
    try:
        with conn.cursor() as cursor:
            # 读取并执行 seed_data.sql
            with open('database/seed_data.sql', 'r', encoding='utf-8') as f:
                sql_commands = f.read()
                for command in sql_commands.split(';'):
                    if command.strip():
                        cursor.execute(command)
            
            conn.commit()
            print("示例数据插入成功")
    finally:
        conn.close()

if __name__ == '__main__':
    print("开始初始化数据库...")
    init_database()
    print("开始插入示例数据...")
    insert_sample_data()
    print("数据库初始化完成！")
```

2. **创建 `seed_data.sql`**（示例数据）：
```sql
-- 插入示例用户
INSERT INTO users (username, email, password_hash, preferences, avatar_url) VALUES
('admin', 'admin@example.com', '$2b$12$1NyQcwAeC7BzJUZKPMYyQOXaLMWS3TlRXLi/7r4MUf1ZWn1NqvwUe', '{"interests": ["历史", "美食", "摄影"], "travel_style": "文化探索"}', '/static/uploads/avatars/admin.jpg'),
('test_user', 'test@example.com', '$2b$12$rHpELs.ufMT9d4CnYmMkUuS5JwENACzUj9L4FMn0S1ZCDUxVFZaJC', '{"interests": ["自然", "徒步", "摄影"], "travel_style": "户外探险"}', '/static/uploads/avatars/test_user.jpg');

-- 插入示例景点
INSERT INTO places (name, description, location_lat, location_lng, category, images, rating, visit_time, tags) VALUES
('故宫博物院', '中国明清两代的皇家宫殿，世界上现存规模最大、保存最为完整的木质结构古建筑之一', 39.91667, 116.39722, '历史遗迹', '["static/uploads/places/forbidden_city_1.jpg", "static/uploads/places/forbidden_city_2.jpg"]', 4.8, 180, '["世界文化遗产", "古代建筑", "博物馆", "人气景点"]'),
('西湖', '中国浙江省杭州市西湖区龙井路1号，中国大陆首批国家重点风景名胜区和中国十大风景名胜之一', 30.25924, 120.14989, '自然景观', '["static/uploads/places/west_lake_1.jpg", "static/uploads/places/west_lake_2.jpg"]', 4.9, 240, '["世界文化遗产", "湖泊", "园林", "摄影胜地"]');

-- 插入示例美食
INSERT INTO foods (name, description, location_lat, location_lng, category, images, price_level, rating, tags, business_hours) VALUES
('北京烤鸭', '北京烤鸭是具有世界声誉的北京著名菜式，用料为优质肉食鸭北京鸭，果木炭火烤制，色泽红润，肉质肥而不腻', 39.90882, 116.40739, '京菜', '["static/uploads/foods/peking_duck_1.jpg", "static/uploads/foods/peking_duck_2.jpg"]', 4, 4.7, '["招牌菜", "传统美食", "必吃"]', '{"周一至周日": "11:00-22:00"}'),
('杭州西湖醋鱼', '西湖醋鱼是浙江省杭州市的传统名菜，属于浙菜系，是中国国家级非物质文化遗产之一', 30.25628, 120.15197, '浙菜', '["static/uploads/foods/west_lake_fish_1.jpg", "static/uploads/foods/west_lake_fish_2.jpg"]', 3, 4.6, '["传统名菜", "当地特色", "推荐"]', '{"周一至周日": "10:30-21:30"}');
```

---

## 3. 爬虫数据采集
**`crawler/`**

> **目标**：从开放数据源获取景点、美食和地图数据。

### 开发步骤

#### 3.1 OpenStreetMap 数据爬取

1. **创建 `scrape_osm.py`**：
```python
import os
import sys
import json
import requests
import time
import pandas as pd
from tqdm import tqdm

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 创建数据目录
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(data_dir, exist_ok=True)

def get_osm_data(bbox, amenities):
    """从 OpenStreetMap 获取指定区域内的设施数据
    
    Args:
        bbox (tuple): 边界框坐标 (min_lat, min_lon, max_lat, max_lon)
        amenities (list): 设施类型列表，如 ['restaurant', 'cafe', 'hotel']
        
    Returns:
        dict: 包含各类设施数据的字典
    """
    base_url = "https://overpass-api.de/api/interpreter"
    results = {}
    
    for amenity in tqdm(amenities, desc="获取 OSM 数据"):
        # 构建 Overpass QL 查询
        query = f"""
        [out:json];
        (
          node["amenity"="{amenity}"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
          way["amenity"="{amenity}"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
          relation["amenity"="{amenity}"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
        );
        out center;
        """
        
        # 发送请求
        try:
            response = requests.post(base_url, data={"data": query})
            response.raise_for_status()
            data = response.json()
            results[amenity] = data
            
            # 保存到文件
            with open(os.path.join(data_dir, f"osm_{amenity}.json"), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            # 避免请求过于频繁
            time.sleep(2)
            
        except Exception as e:
            print(f"获取 {amenity} 数据时出错: {e}")
    
    return results

def process_osm_data(results):
    """处理 OSM 数据，提取有用信息
    
    Args:
        results (dict): 从 OSM 获取的原始数据
        
    Returns:
        dict: 处理后的数据
    """
    processed_data = {}
    
    for amenity, data in results.items():
        elements = data.get('elements', [])
        items = []
        
        for element in elements:
            # 提取基本信息
            item = {
                'id': element.get('id'),
                'type': element.get('type'),
                'tags': element.get('tags', {}),
                'name': element.get('tags', {}).get('name'),
                'amenity': element.get('tags', {}).get('amenity')
            }
            
            # 提取位置信息
            if element.get('type') == 'node':
                item['lat'] = element.get('lat')
                item['lon'] = element.get('lon')
            elif 'center' in element:
                item['lat'] = element.get('center', {}).get('lat')
                item['lon'] = element.get('center', {}).get('lon')
            
            # 只保留有名称的项目
            if item['name']:
                items.append(item)
        
        processed_data[amenity] = items
        
        # 保存处理后的数据
        with open(os.path.join(data_dir, f"processed_osm_{amenity}.json"), 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
    
    return processed_data

def main():
    # 定义要爬取的区域（