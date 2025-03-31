from datetime import datetime
from sqlalchemy import func
from . import db

class Place(db.Model):
    """景点模型类
    包含景点基本信息和特征字段
    """
    __tablename__ = 'places'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    # 位置坐标
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(200))
    city = db.Column(db.String(50), index=True)
    province = db.Column(db.String(50), index=True)
    country = db.Column(db.String(50), index=True)
    # 开放时间
    opening_hours = db.Column(db.String(200))
    # 门票价格
    ticket_price = db.Column(db.Float)
    # 联系电话
    contact_phone = db.Column(db.String(20))
    # 官方网站
    website = db.Column(db.String(200))
    
    # 特征字段
    # 景点类型 (自然景观、历史遗迹、主题公园等)
    place_type = db.Column(db.String(50), index=True)
    # 标签 - 使用JSON类型存储多个标签
    tags = db.Column(db.JSON, default=list)
    # 评分 (1-5分)
    rating = db.Column(db.Float, default=0.0)
    # 评价数量
    review_count = db.Column(db.Integer, default=0)
    # 热度/人气
    popularity = db.Column(db.Integer, default=0)
    # 适合季节 (春夏秋冬)
    suitable_seasons = db.Column(db.JSON, default=list)
    # 推荐游玩时长(小时)
    recommended_visit_time = db.Column(db.Float)
    # 景点图片URL列表
    images = db.Column(db.JSON, default=list)
    
    # 创建和更新时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, name, latitude, longitude, **kwargs):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        
        # 处理其他可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self):
        return f'<Place {self.name}> at ({self.latitude}, {self.longitude})'
    
    @staticmethod
    def get_nearby_places(latitude, longitude, radius=5.0, limit=10):
        """获取指定坐标附近的景点
        
        Args:
            latitude: 纬度
            longitude: 经度
            radius: 搜索半径(公里)
            limit: 返回结果数量限制
            
        Returns:
            附近景点列表
        """
        # 使用Haversine公式计算距离
        # 地球半径(公里)
        earth_radius = 6371.0
        
        # 将半径转换为弧度
        radius_in_radians = radius / earth_radius
        
        # 计算距离并筛选
        distance = func.acos(
            func.sin(func.radians(latitude)) * func.sin(func.radians(Place.latitude)) +
            func.cos(func.radians(latitude)) * func.cos(func.radians(Place.latitude)) *
            func.cos(func.radians(Place.longitude) - func.radians(longitude))
        ) * earth_radius
        
        nearby_places = Place.query.filter(
            distance <= radius
        ).order_by(distance).limit(limit).all()
        
        return nearby_places
    
    @staticmethod
    def search_by_type_and_tags(place_type=None, tags=None, city=None, limit=20):
        """根据类型和标签搜索景点
        
        Args:
            place_type: 景点类型
            tags: 标签列表
            city: 城市名称
            limit: 返回结果数量限制
            
        Returns:
            符合条件的景点列表
        """
        query = Place.query
        
        if place_type:
            query = query.filter(Place.place_type == place_type)
        
        if city:
            query = query.filter(Place.city == city)
        
        if tags:
            # 对于每个标签，筛选包含该标签的景点
            for tag in tags:
                query = query.filter(Place.tags.contains([tag]))
        
        return query.limit(limit).all()