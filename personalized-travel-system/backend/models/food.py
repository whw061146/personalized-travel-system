from datetime import datetime
from sqlalchemy import func
from . import db

class Food(db.Model):
    """美食模型类
    包含美食基本信息和餐厅信息
    """
    __tablename__ = 'foods'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    # 价格范围 (1-5，1最低，5最高)
    price_level = db.Column(db.Integer, default=3)
    # 美食类型 (中餐、西餐、日料等)
    cuisine_type = db.Column(db.String(50), index=True)
    # 口味特点 (辣、甜、酸等)
    taste_tags = db.Column(db.JSON, default=list)
    # 特色菜品
    signature_dishes = db.Column(db.JSON, default=list)
    
    # 餐厅信息
    restaurant_name = db.Column(db.String(100), index=True)
    # 位置坐标
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(200))
    city = db.Column(db.String(50), index=True)
    province = db.Column(db.String(50), index=True)
    country = db.Column(db.String(50), index=True)
    # 营业时间
    opening_hours = db.Column(db.String(200))
    # 联系电话
    contact_phone = db.Column(db.String(20))
    # 官方网站
    website = db.Column(db.String(200))
    
    # 特征字段
    # 评分 (1-5分)
    rating = db.Column(db.Float, default=0.0)
    # 评价数量
    review_count = db.Column(db.Integer, default=0)
    # 人均消费
    average_cost = db.Column(db.Float)
    # 适合场景 (家庭聚餐、商务宴请、朋友聚会等)
    suitable_occasions = db.Column(db.JSON, default=list)
    # 餐厅图片URL列表
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
        return f'<Food {self.name}> at ({self.latitude}, {self.longitude})'
    
    @staticmethod
    def get_nearby_foods(latitude, longitude, radius=5.0, limit=10):
        """获取指定坐标附近的美食
        
        Args:
            latitude: 纬度
            longitude: 经度
            radius: 搜索半径(公里)
            limit: 返回结果数量限制
            
        Returns:
            附近美食列表
        """
        # 使用Haversine公式计算距离
        # 地球半径(公里)
        earth_radius = 6371.0
        
        # 将半径转换为弧度
        radius_in_radians = radius / earth_radius
        
        # 计算距离并筛选
        distance = func.acos(
            func.sin(func.radians(latitude)) * func.sin(func.radians(Food.latitude)) +
            func.cos(func.radians(latitude)) * func.cos(func.radians(Food.latitude)) *
            func.cos(func.radians(Food.longitude) - func.radians(longitude))
        ) * earth_radius
        
        nearby_foods = Food.query.filter(
            distance <= radius
        ).order_by(distance).limit(limit).all()
        
        return nearby_foods
    
    @staticmethod
    def search_by_type_and_taste(cuisine_type=None, taste_tags=None, city=None, price_level=None, limit=20):
        """根据类型和口味搜索美食
        
        Args:
            cuisine_type: 美食类型
            taste_tags: 口味标签列表
            city: 城市名称
            price_level: 价格等级
            limit: 返回结果数量限制
            
        Returns:
            符合条件的美食列表
        """
        query = Food.query
        
        if cuisine_type:
            query = query.filter(Food.cuisine_type == cuisine_type)
        
        if city:
            query = query.filter(Food.city == city)
        
        if price_level:
            query = query.filter(Food.price_level == price_level)
        
        if taste_tags:
            # 对于每个口味标签，筛选包含该标签的美食
            for tag in taste_tags:
                query = query.filter(Food.taste_tags.contains([tag]))
        
        return query.limit(limit).all()