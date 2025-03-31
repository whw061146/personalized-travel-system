from datetime import datetime
from . import db

class Diary(db.Model):
    """旅游日记模型类
    包含日记内容、创建时间、关联用户等字段
    添加图片、位置标记等功能
    实现日记分享和隐私控制
    """
    __tablename__ = 'diaries'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    # 创建和更新时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 位置标记
    location_name = db.Column(db.String(100))  # 位置名称
    latitude = db.Column(db.Float)  # 纬度
    longitude = db.Column(db.Float)  # 经度
    address = db.Column(db.String(200))  # 详细地址
    city = db.Column(db.String(50))  # 城市
    province = db.Column(db.String(50))  # 省份
    country = db.Column(db.String(50))  # 国家
    
    # 图片URL列表，使用JSON类型存储多个图片URL
    images = db.Column(db.JSON, default=list)
    
    # 隐私设置
    is_public = db.Column(db.Boolean, default=True)  # 是否公开
    allow_comments = db.Column(db.Boolean, default=True)  # 是否允许评论
    
    # 统计数据
    view_count = db.Column(db.Integer, default=0)  # 浏览次数
    like_count = db.Column(db.Integer, default=0)  # 点赞次数
    comment_count = db.Column(db.Integer, default=0)  # 评论次数
    
    # 关联用户（作者）
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 标签 - 使用JSON类型存储多个标签
    tags = db.Column(db.JSON, default=list)
    
    def __init__(self, title, content, user_id, **kwargs):
        self.title = title
        self.content = content
        self.user_id = user_id
        
        # 处理其他可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self):
        """将日记信息转换为字典，用于API响应"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'location_name': self.location_name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'address': self.address,
            'city': self.city,
            'province': self.province,
            'country': self.country,
            'images': self.images,
            'is_public': self.is_public,
            'allow_comments': self.allow_comments,
            'view_count': self.view_count,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'user_id': self.user_id,
            'tags': self.tags
        }
    
    def increment_view_count(self):
        """增加浏览次数"""
        self.view_count += 1
        db.session.commit()
    
    def toggle_like(self):
        """切换点赞状态"""
        self.like_count += 1
        db.session.commit()
    
    def update_comment_count(self):
        """更新评论数量"""
        # 这里可以实现评论数量的计算逻辑
        # 例如从关联的评论表中统计
        db.session.commit()
    
    def toggle_privacy(self):
        """切换隐私状态"""
        self.is_public = not self.is_public
        db.session.commit()
    
    def toggle_comments_permission(self):
        """切换评论权限"""
        self.allow_comments = not self.allow_comments
        db.session.commit()
    
    def __repr__(self):
        return f'<Diary {self.title}>'