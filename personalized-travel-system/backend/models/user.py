from flask_bcrypt import generate_password_hash, check_password_hash
from datetime import datetime
from . import db

class User(db.Model):
    """用户模型类
    包含用户基本信息和偏好设置
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    avatar = db.Column(db.String(200))  # 头像URL
    bio = db.Column(db.Text)  # 个人简介
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    # 用户偏好字段
    # 旅游偏好 - 使用JSON类型存储多个偏好标签
    travel_preferences = db.Column(db.JSON, default=list)
    # 美食偏好 - 使用JSON类型存储多个偏好标签
    food_preferences = db.Column(db.JSON, default=list)
    # 预算范围 (1-5，1最低，5最高)
    budget_level = db.Column(db.Integer, default=3)
    # 出行方式偏好 (步行、公交、自驾等)
    transportation_preference = db.Column(db.String(50))
    # 住宿偏好 (经济型、舒适型、豪华型等)
    accommodation_preference = db.Column(db.String(50))
    
    # 关联关系
    diaries = db.relationship('Diary', backref='author', lazy='dynamic')
    
    def __init__(self, username, email, password, **kwargs):
        self.username = username
        self.email = email
        self.set_password(password)
        
        # 处理其他可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """将用户信息转换为字典，用于API响应"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'avatar': self.avatar,
            'bio': self.bio,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'travel_preferences': self.travel_preferences,
            'food_preferences': self.food_preferences,
            'budget_level': self.budget_level,
            'transportation_preference': self.transportation_preference,
            'accommodation_preference': self.accommodation_preference
        }
    
    def __repr__(self):
        return f'<User {self.username}>'