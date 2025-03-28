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
    tags JSON,  -- ��ǩJSON���飨��"�ʺ�����"��"�����徲
