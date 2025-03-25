from . import db
from datetime import datetime

class User(db.Model):
    """用户模型：存储用户基本信息和认证信息"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    avatar_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 用户偏好（可选）
    preferences = db.Column(db.JSON, nullable=True)
    
    # 关系
    # 这里可以添加与其他模型的关系，如用户的旅行日记、收藏等
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        """将用户对象转换为字典，用于API响应"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'preferences': self.preferences
        }