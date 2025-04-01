import math
from typing import List, Dict, Any, Optional, Tuple, Union
from flask import request, jsonify
from sqlalchemy.orm import Query

# 距离计算函数
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    使用Haversine公式计算两点之间的距离（单位：公里）
    
    Args:
        lat1: 第一个点的纬度
        lon1: 第一个点的经度
        lat2: 第二个点的纬度
        lon2: 第二个点的经度
        
    Returns:
        两点之间的距离（公里）
    """
    # 地球半径（公里）
    earth_radius = 6371.0
    
    # 将经纬度转换为弧度
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # 纬度和经度的差值
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine公式
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = earth_radius * c
    
    return distance

# 数据格式转换工具
def to_dict(obj: Any, exclude: List[str] = None) -> Dict[str, Any]:
    """
    将SQLAlchemy模型对象转换为字典
    
    Args:
        obj: SQLAlchemy模型对象
        exclude: 需要排除的字段列表
        
    Returns:
        转换后的字典
    """
    if exclude is None:
        exclude = []
        
    result = {}
    for column in obj.__table__.columns:
        if column.name not in exclude:
            result[column.name] = getattr(obj, column.name)
    
    return result

def format_response(status: str, data: Any = None, message: str = None, code: int = 200) -> Tuple[Dict[str, Any], int]:
    """
    格式化API响应
    
    Args:
        status: 状态（success或error）
        data: 响应数据
        message: 响应消息
        code: HTTP状态码
        
    Returns:
        格式化的响应和HTTP状态码
    """
    response = {
        'status': status
    }
    
    if data is not None:
        response['data'] = data
        
    if message is not None:
        response['message'] = message
        
    return jsonify(response), code

# 分页功能
def paginate(query: Query, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
    """
    对查询结果进行分页
    
    Args:
        query: SQLAlchemy查询对象
        page: 页码（从1开始）
        per_page: 每页项目数
        
    Returns:
        包含分页信息和结果的字典
    """
    # 确保页码和每页数量为正整数
    page = max(1, page)
    per_page = max(1, per_page)
    
    # 计算总数
    total = query.count()
    
    # 计算总页数
    total_pages = (total + per_page - 1) // per_page
    
    # 获取当前页的数据
    items = query.limit(per_page).offset((page - 1) * per_page).all()
    
    # 构建分页信息
    pagination = {
        'items': items,
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages,
        'has_next': page < total_pages,
        'has_prev': page > 1
    }
    
    return pagination

def get_pagination_params() -> Tuple[int, int]:
    """
    从请求参数中获取分页参数
    
    Returns:
        (页码, 每页数量)元组
    """
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    
    # 确保页码和每页数量为正整数
    page = max(1, page)
    per_page = max(1, min(100, per_page))  # 限制每页最大数量为100
    
    return page, per_page