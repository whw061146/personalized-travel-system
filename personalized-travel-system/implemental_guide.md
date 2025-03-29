# ���Ի������Ƽ�ϵͳ - ʵ��ָ��

## ��Ŀ�������� & ����ջ

��ָ����ϸ������ΰ��� **��� �� ���ݿ� �� ���� �� AI �� ǰ�� �� ����** ��˳�򿪷� **���Ի������Ƽ�ϵͳ**��

---

## 1. ���˿�ܣ�Flask��
**`backend/`**

> **Ŀ��**��� Flask Ӧ�ã��������ݿ⣬ע�� API ·�ɡ�

### ��������

#### 1.1 ��������Ӧ�ýṹ
1. **���� `app.py`**��Flask ����ڣ���
```python
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from routes import register_blueprints
from models import db
import config

app = Flask(__name__)

# ��������
app.config.from_object(config.Config)

# ��ʼ����չ
db.init_app(app)
CORS(app)
jwt = JWTManager(app)

# ע��������ͼ
register_blueprints(app)

@app.route('/api/health')
def health_check():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

2. **���� `config.py`**���������ݿ⡢JWT ��Կ����
```python
import os
from datetime import timedelta

class Config:
    # ���ݿ�����
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@localhost/travel_system'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT����
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # �ϴ��ļ�����
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB ����ϴ�����
```

3. **��д `requirements.txt`**����װ������������
```
# Web��ܺ���չ
Flask==2.0.1
Flask-SQLAlchemy==2.5.1
Flask-JWT-Extended==4.3.1
Flask-CORS==3.0.10
Flask-RESTful==0.3.9
Flask-Migrate==3.1.0
Werkzeug==2.0.1
gunicorn==20.1.0

# ���ݿ�����
PyMySQL==1.0.2
SQLAlchemy==1.4.23

# ��֤�밲ȫ
passlib==1.7.4
email-validator==1.1.3
pyjwt==2.1.0

# ��������������
requests==2.26.0
BeautifulSoup4==4.10.0
Selenium==4.0.0
lxml==4.6.3

# ���ݴ��������
numpy==1.21.2
pandas==1.3.3
matplotlib==3.4.3
seaborn==0.11.2

# ����ѧϰ��AI
scikit-learn==1.0
gensim==4.1.2
tensorflow==2.6.0
keras==2.6.0
faiss-cpu==1.7.1

# ͼ����
pillow==8.3.2
opencv-python==4.5.3

# ���߿�
python-dotenv==0.19.0
tqdm==4.62.2
joblib==1.0.1
pytz==2021.1
```

#### 1.2 ������ݿ�ģ��

4. **��ʼ�� `schema.sql`**������ MySQL ��ṹ����
```sql
CREATE DATABASE IF NOT EXISTS travel_system;
USE travel_system;

-- �û���
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    preferences JSON,  -- �洢�û�ƫ�õ�JSON����
    avatar_url VARCHAR(255)
);

-- �����
CREATE TABLE IF NOT EXISTS places (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    location_lat DECIMAL(10, 8) NOT NULL,
    location_lng DECIMAL(11, 8) NOT NULL,
    category VARCHAR(50),  -- ���������Ȼ���ۡ���ʷ�ż��ȣ�
    images JSON,  -- �洢ͼƬURL��JSON����
    rating DECIMAL(2, 1),  -- ���֣�1-5�֣�
    visit_time INT,  -- ��������ʱ�䣨���ӣ�
    tags JSON,  -- ��ǩJSON���飨��"�ʺ�����"��"�����徲"��
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ��ʳ��
CREATE TABLE IF NOT EXISTS foods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    location_lat DECIMAL(10, 8) NOT NULL,
    location_lng DECIMAL(11, 8) NOT NULL,
    category VARCHAR(50),  -- ��ʳ����紨�ˡ����˵ȣ�
    images JSON,  -- �洢ͼƬURL��JSON����
    price_level TINYINT,  -- �۸�ȼ���1-5��
    rating DECIMAL(2, 1),  -- ���֣�1-5�֣�
    tags JSON,  -- ��ǩJSON���飨��"���Ʋ�"��"��������"��
    business_hours JSON,  -- Ӫҵʱ��JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- �����ռǱ�
CREATE TABLE IF NOT EXISTS diaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    content TEXT,
    images JSON,  -- �洢ͼƬURL��JSON����
    location_lat DECIMAL(10, 8),
    location_lng DECIMAL(11, 8),
    visit_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- �û��ղر�
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

-- �û����ֱ�
CREATE TABLE IF NOT EXISTS ratings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    place_id INT,
    food_id INT,
    rating DECIMAL(2, 1) NOT NULL,  -- ���֣�1-5�֣�
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE,
    FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE CASCADE
);

-- ·���滮��
CREATE TABLE IF NOT EXISTS paths (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100),
    places JSON,  -- �洢����ID��JSON����
    path_data JSON,  -- �洢·�����ݵ�JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

5. **���� SQLAlchemy ORM ģ��**��`models/user.py`����
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
    
    # ��ϵ
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

#### 1.3 ʵ�� API ·��

6. **���� Blueprint ��ʼ��**��`routes/__init__.py`����
```python
from flask import Blueprint

# ������ͼ
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
recommend_bp = Blueprint('recommend', __name__, url_prefix='/api/recommend')
search_bp = Blueprint('search', __name__, url_prefix='/api/search')
map_bp = Blueprint('map', __name__, url_prefix='/api/map')
diary_bp = Blueprint('diary', __name__, url_prefix='/api/diary')
food_bp = Blueprint('food', __name__, url_prefix='/api/food')
indoor_bp = Blueprint('indoor', __name__, url_prefix='/api/indoor')
aigc_bp = Blueprint('aigc', __name__, url_prefix='/api/aigc')

# ����·�ɴ�����
from . import auth, recommend, search, map, diary, food, indoor, aigc

def register_blueprints(app):
    """ע��������ͼ��Ӧ��"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(recommend_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(map_bp)
    app.register_blueprint(diary_bp)
    app.register_blueprint(food_bp)
    app.register_blueprint(indoor_bp)
    app.register_blueprint(aigc_bp)
```

7. **ʵ����֤ API**��`routes/auth.py`����
```python
from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from . import auth_bp
from models.user import User
from models import db

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # ��֤�����ֶ�
    if not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({'error': 'ȱ�ٱ����ֶ�'}), 400
    
    # ����û����������Ƿ��Ѵ���
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '�û����Ѵ���'}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': '������ע��'}), 409
    
    # �������û�
    user = User(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        preferences=data.get('preferences'),
        avatar_url=data.get('avatar_url')
    )
    
    db.session.add(user)
    db.session.commit()
    
    # ���ɷ�������
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': 'ע��ɹ�',
        'access_token': access_token,
        'user': user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # ��֤�����ֶ�
    if not all(k in data for k in ('username', 'password')):
        return jsonify({'error': 'ȱ�ٱ����ֶ�'}), 400
    
    # �����û�
    user = User.query.filter_by(username=data['username']).first()
    
    # ��֤����
    if not user or not user.check_password(data['password']):
        return jsonify({'error': '�û������������'}), 401
    
    # ���ɷ�������
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': '��¼�ɹ�',
        'access_token': access_token,
        'user': user.to_dict()
    })

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': '�û�������'}), 404
    
    return jsonify(user.to_dict())

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': '�û�������'}), 404
    
    data = request.get_json()
    
    # �����û���Ϣ
    if 'username' in data and data['username'] != user.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': '�û����Ѵ���'}), 409
        user.username = data['username']
    
    if 'email' in data and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': '������ע��'}), 409
        user.email = data['email']
    
    if 'password' in data:
        user.set_password(data['password'])
    
    if 'preferences' in data:
        user.preferences = data['preferences']
    
    if 'avatar_url' in data:
        user.avatar_url = data['avatar_url']
    
    db.session.commit()
    
    return jsonify({
        'message': '������Ϣ���³ɹ�',
        'user': user.to_dict()
    })
```

---

## 2. ���ݿ�������ʼ��
**`database/`**

> **Ŀ��**����ʼ�����ݿ⣬������ṹ������ʾ�����ݡ�

### ��������

#### 2.1 ���ݿ��ʼ���ű�

1. **���� `init_db.py`**��
```python
import os
import sys
import pymysql
import json
from datetime import datetime

# �����Ŀ��Ŀ¼�� Python ·��
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ��������
from backend.config import Config

def init_database():
    """��ʼ�����ݿ�ͱ�ṹ"""
    # �������ݿ������ַ���
    db_uri = Config.SQLALCHEMY_DATABASE_URI
    db_info = db_uri.replace('mysql+pymysql://', '').split('@')[0].split(':')
    username = db_info[0]
    password = db_info[1].split('/')[0]
    host = db_uri.split('@')[1].split('/')[0]
    database = db_uri.split('/')[-1]
    
    # ���� MySQL����ָ�����ݿ⣩
    conn = pymysql.connect(
        host=host,
        user=username,
        password=password,
        charset='utf8mb4'
    )
    
    try:
        with conn.cursor() as cursor:
            # �������ݿ�
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute(f"USE {database}")
            
            # ��ȡ��ִ�� schema.sql
            with open('backend/schema.sql', 'r', encoding='utf-8') as f:
                sql_commands = f.read()
                for command in sql_commands.split(';'):
                    if command.strip():
                        cursor.execute(command)
            
            conn.commit()
            print(f"���ݿ� {database} �ͱ�ṹ�����ɹ�")
    finally:
        conn.close()

def insert_sample_data():
    """����ʾ������"""
    # ���ӵ��Ѵ��������ݿ�
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
            # ��ȡ��ִ�� seed_data.sql
            with open('database/seed_data.sql', 'r', encoding='utf-8') as f:
                sql_commands = f.read()
                for command in sql_commands.split(';'):
                    if command.strip():
                        cursor.execute(command)
            
            conn.commit()
            print("ʾ�����ݲ���ɹ�")
    finally:
        conn.close()

if __name__ == '__main__':
    print("��ʼ��ʼ�����ݿ�...")
    init_database()
    print("��ʼ����ʾ������...")
    insert_sample_data()
    print("���ݿ��ʼ����ɣ�")
```

2. **���� `seed_data.sql`**��ʾ�����ݣ���
```sql
-- ����ʾ���û�
INSERT INTO users (username, email, password_hash, preferences, avatar_url) VALUES
('admin', 'admin@example.com', '$2b$12$1NyQcwAeC7BzJUZKPMYyQOXaLMWS3TlRXLi/7r4MUf1ZWn1NqvwUe', '{"interests": ["��ʷ", "��ʳ", "��Ӱ"], "travel_style": "�Ļ�̽��"}', '/static/uploads/avatars/admin.jpg'),
('test_user', 'test@example.com', '$2b$12$rHpELs.ufMT9d4CnYmMkUuS5JwENACzUj9L4FMn0S1ZCDUxVFZaJC', '{"interests": ["��Ȼ", "ͽ��", "��Ӱ"], "travel_style": "����̽��"}', '/static/uploads/avatars/test_user.jpg');

-- ����ʾ������
INSERT INTO places (name, description, location_lat, location_lng, category, images, rating, visit_time, tags) VALUES
('�ʹ�����Ժ', '�й����������Ļʼҹ���������ִ��ģ��󡢱�����Ϊ������ľ�ʽṹ�Ž���֮һ', 39.91667, 116.39722, '��ʷ�ż�', '["static/uploads/places/forbidden_city_1.jpg", "static/uploads/places/forbidden_city_2.jpg"]', 4.8, 180, '["�����Ļ��Ų�", "�Ŵ�����", "�����", "��������"]'),
('����', '�й��㽭ʡ����������������·1�ţ��й���½���������ص�羰��ʤ�����й�ʮ��羰��ʤ֮һ', 30.25924, 120.14989, '��Ȼ����', '["static/uploads/places/west_lake_1.jpg", "static/uploads/places/west_lake_2.jpg"]', 4.9, 240, '["�����Ļ��Ų�", "����", "԰��", "��Ӱʤ��"]');

-- ����ʾ����ʳ
INSERT INTO foods (name, description, location_lat, location_lng, category, images, price_level, rating, tags, business_hours) VALUES
('������Ѽ', '������Ѽ�Ǿ������������ı���������ʽ������Ϊ������ʳѼ����Ѽ����ľ̿���ƣ�ɫ��������ʷʶ�����', 39.90882, 116.40739, '����', '["static/uploads/foods/peking_duck_1.jpg", "static/uploads/foods/peking_duck_2.jpg"]', 4, 4.7, '["���Ʋ�", "��ͳ��ʳ", "�س�"]', '{"��һ������": "11:00-22:00"}'),
('������������', '�����������㽭ʡ�����еĴ�ͳ���ˣ��������ϵ�����й����Ҽ��������Ļ��Ų�֮һ', 30.25628, 120.15197, '���', '["static/uploads/foods/west_lake_fish_1.jpg", "static/uploads/foods/west_lake_fish_2.jpg"]', 3, 4.6, '["��ͳ����", "������ɫ", "�Ƽ�"]', '{"��һ������": "10:30-21:30"}');
```

---

## 3. �������ݲɼ�
**`crawler/`**

> **Ŀ��**���ӿ�������Դ��ȡ���㡢��ʳ�͵�ͼ���ݡ�

### ��������

#### 3.1 OpenStreetMap ������ȡ

1. **���� `scrape_osm.py`**��
```python
import os
import sys
import json
import requests
import time
import pandas as pd
from tqdm import tqdm

# �����Ŀ��Ŀ¼�� Python ·��
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ��������Ŀ¼
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(data_dir, exist_ok=True)

def get_osm_data(bbox, amenities):
    """�� OpenStreetMap ��ȡָ�������ڵ���ʩ����
    
    Args:
        bbox (tuple): �߽������ (min_lat, min_lon, max_lat, max_lon)
        amenities (list): ��ʩ�����б��� ['restaurant', 'cafe', 'hotel']
        
    Returns:
        dict: ����������ʩ���ݵ��ֵ�
    """
    base_url = "https://overpass-api.de/api/interpreter"
    results = {}
    
    for amenity in tqdm(amenities, desc="��ȡ OSM ����"):
        # ���� Overpass QL ��ѯ
        query = f"""
        [out:json];
        (
          node["amenity"="{amenity}"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
          way["amenity"="{amenity}"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
          relation["amenity"="{amenity}"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
        );
        out center;
        """
        
        # ��������
        try:
            response = requests.post(base_url, data={"data": query})
            response.raise_for_status()
            data = response.json()
            results[amenity] = data
            
            # ���浽�ļ�
            with open(os.path.join(data_dir, f"osm_{amenity}.json"), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            # �����������Ƶ��
            time.sleep(2)
            
        except Exception as e:
            print(f"��ȡ {amenity} ����ʱ����: {e}")
    
    return results

def process_osm_data(results):
    """���� OSM ���ݣ���ȡ������Ϣ
    
    Args:
        results (dict): �� OSM ��ȡ��ԭʼ����
        
    Returns:
        dict: ����������
    """
    processed_data = {}
    
    for amenity, data in results.items():
        elements = data.get('elements', [])
        items = []
        
        for element in elements:
            # ��ȡ������Ϣ
            item = {
                'id': element.get('id'),
                'type': element.get('type'),
                'tags': element.get('tags', {}),
                'name': element.get('tags', {}).get('name'),
                'amenity': element.get('tags', {}).get('amenity')
            }
            
            # ��ȡλ����Ϣ
            if element.get('type') == 'node':
                item['lat'] = element.get('lat')
                item['lon'] = element.get('lon')
            elif 'center' in element:
                item['lat'] = element.get('center', {}).get('lat')
                item['lon'] = element.get('center', {}).get('lon')
            
            # ֻ���������Ƶ���Ŀ
            if item['name']:
                items.append(item)
        
        processed_data[amenity] = items
        
        # ���洦��������
        with open(os.path.join(data_dir, f"processed_osm_{amenity}.json"), 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
    
    return processed_data

def main():
    # ����Ҫ��ȡ������