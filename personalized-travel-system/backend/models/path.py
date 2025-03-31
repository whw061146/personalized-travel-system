from datetime import datetime
from sqlalchemy import func
from . import db

class Path(db.Model):
    """路径规划模型类
    包含路径点、距离、时间等信息
    实现路径优化算法
    """
    __tablename__ = 'paths'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)  # 路径名称
    description = db.Column(db.Text)  # 路径描述
    
    # 路径基本信息
    total_distance = db.Column(db.Float, default=0.0)  # 总距离(公里)
    total_time = db.Column(db.Float, default=0.0)  # 总时间(分钟)
    start_point = db.Column(db.String(100))  # 起点名称
    end_point = db.Column(db.String(100))  # 终点名称
    
    # 起点坐标
    start_latitude = db.Column(db.Float, nullable=False)
    start_longitude = db.Column(db.Float, nullable=False)
    # 终点坐标
    end_latitude = db.Column(db.Float, nullable=False)
    end_longitude = db.Column(db.Float, nullable=False)
    
    # 路径点 - 使用JSON类型存储路径点列表
    # 每个路径点包含：{"name": "地点名", "lat": 纬度, "lng": 经度, "stay_time": 停留时间(分钟)}
    path_points = db.Column(db.JSON, default=list)
    
    # 交通方式 (步行、公交、自驾等)
    transportation_mode = db.Column(db.String(50), default='walking')
    
    # 路径特征
    is_optimized = db.Column(db.Boolean, default=False)  # 是否已优化
    has_traffic = db.Column(db.Boolean, default=False)  # 是否考虑交通状况
    avoid_highways = db.Column(db.Boolean, default=False)  # 是否避开高速
    avoid_tolls = db.Column(db.Boolean, default=False)  # 是否避开收费路段
    
    # 关联用户（创建者）
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # 创建和更新时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, name, start_latitude, start_longitude, end_latitude, end_longitude, **kwargs):
        self.name = name
        self.start_latitude = start_latitude
        self.start_longitude = start_longitude
        self.end_latitude = end_latitude
        self.end_longitude = end_longitude
        
        # 处理其他可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def add_path_point(self, name, latitude, longitude, stay_time=0):
        """添加路径点"""
        if self.path_points is None:
            self.path_points = []
            
        point = {
            "name": name,
            "lat": latitude,
            "lng": longitude,
            "stay_time": stay_time
        }
        
        self.path_points.append(point)
        self._update_path_metrics()
        return self
    
    def remove_path_point(self, index):
        """移除指定索引的路径点"""
        if self.path_points and 0 <= index < len(self.path_points):
            self.path_points.pop(index)
            self._update_path_metrics()
        return self
    
    def _update_path_metrics(self):
        """更新路径的总距离和总时间"""
        # 计算总距离和总时间
        total_distance = 0.0
        total_time = 0.0
        
        # 添加起点到第一个路径点的距离
        if self.path_points and len(self.path_points) > 0:
            first_point = self.path_points[0]
            total_distance += self._calculate_distance(
                self.start_latitude, self.start_longitude,
                first_point["lat"], first_point["lng"]
            )
            
            # 计算路径点之间的距离
            for i in range(len(self.path_points) - 1):
                point1 = self.path_points[i]
                point2 = self.path_points[i + 1]
                
                distance = self._calculate_distance(
                    point1["lat"], point1["lng"],
                    point2["lat"], point2["lng"]
                )
                
                total_distance += distance
                # 假设平均速度为5km/h步行，计算时间（分钟）
                total_time += (distance / 5) * 60
                
                # 添加停留时间
                total_time += point1["stay_time"]
            
            # 添加最后一个路径点到终点的距离
            last_point = self.path_points[-1]
            total_distance += self._calculate_distance(
                last_point["lat"], last_point["lng"],
                self.end_latitude, self.end_longitude
            )
            
            # 添加最后一个点的停留时间
            total_time += last_point["stay_time"]
        
        self.total_distance = round(total_distance, 2)
        self.total_time = round(total_time, 2)
    
    def _calculate_distance(self, lat1, lng1, lat2, lng2):
        """使用Haversine公式计算两点之间的距离（公里）"""
        from math import radians, sin, cos, sqrt, atan2
        
        # 地球半径（公里）
        R = 6371.0
        
        # 将经纬度转换为弧度
        lat1_rad = radians(lat1)
        lng1_rad = radians(lng1)
        lat2_rad = radians(lat2)
        lng2_rad = radians(lng2)
        
        # 经纬度差值
        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad
        
        # Haversine公式
        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlng / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        
        return distance
    
    def optimize_path(self):
        """优化路径顺序，使用贪心算法"""
        if not self.path_points or len(self.path_points) <= 2:
            # 路径点少于3个，无需优化
            return self
        
        # 起点坐标
        current_lat = self.start_latitude
        current_lng = self.start_longitude
        
        # 未访问的路径点
        unvisited = self.path_points.copy()
        # 优化后的路径点
        optimized_path = []
        
        # 贪心算法：每次选择最近的点
        while unvisited:
            # 找到距离当前位置最近的点
            nearest_idx = 0
            min_distance = float('inf')
            
            for i, point in enumerate(unvisited):
                distance = self._calculate_distance(
                    current_lat, current_lng,
                    point["lat"], point["lng"]
                )
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_idx = i
            
            # 添加最近的点到优化路径
            nearest_point = unvisited.pop(nearest_idx)
            optimized_path.append(nearest_point)
            
            # 更新当前位置
            current_lat = nearest_point["lat"]
            current_lng = nearest_point["lng"]
        
        # 更新路径点
        self.path_points = optimized_path
        self.is_optimized = True
        self._update_path_metrics()
        
        return self
    
    def to_dict(self):
        """将路径转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'total_distance': self.total_distance,
            'total_time': self.total_time,
            'start_point': self.start_point,
            'end_point': self.end_point,
            'start_coordinates': [self.start_latitude, self.start_longitude],
            'end_coordinates': [self.end_latitude, self.end_longitude],
            'path_points': self.path_points,
            'transportation_mode': self.transportation_mode,
            'is_optimized': self.is_optimized,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }