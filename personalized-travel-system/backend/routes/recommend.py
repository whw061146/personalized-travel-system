from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
import random

# 导入数据库和模型
from models import db
from models.user import User
from models.place import Place

# 创建推荐蓝图
recommend_bp = Blueprint('recommend', __name__)

@recommend_bp.route('/places', methods=['GET'])
@jwt_required()
def recommend_places():
    """个性化景点推荐API
    
    基于用户偏好和历史行为推荐景点
    
    Returns:
        推荐景点列表
    """
    # 获取当前用户ID
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({
            'status': 'error',
            'message': '用户不存在'
        }), 404
    
    # 获取查询参数
    limit = request.args.get('limit', default=10, type=int)
    
    # 基于用户偏好推荐
    recommended_places = []
    
    # 如果用户有旅游偏好，根据偏好标签匹配景点
    if user.travel_preferences and len(user.travel_preferences) > 0:
        # 查找与用户偏好标签匹配的景点
        for preference in user.travel_preferences:
            # 在景点标签中查找匹配项
            matching_places = Place.query.filter(
                Place.tags.contains([preference])
            ).order_by(Place.rating.desc()).limit(limit).all()
            
            recommended_places.extend(matching_places)
    
    # 如果推荐列表为空或不足，添加评分最高的景点
    if len(recommended_places) < limit:
        top_rated_places = Place.query.order_by(
            Place.rating.desc()
        ).limit(limit - len(recommended_places)).all()
        
        # 添加到推荐列表，避免重复
        for place in top_rated_places:
            if place not in recommended_places:
                recommended_places.append(place)
    
    # 限制返回数量并转换为字典
    result = [place.to_dict() for place in recommended_places[:limit]]
    
    return jsonify({
        'status': 'success',
        'data': {
            'places': result,
            'count': len(result)
        }
    })

@recommend_bp.route('/places/history', methods=['GET'])
@jwt_required()
def recommend_by_history():
    """基于用户历史的推荐功能
    
    分析用户历史浏览和收藏记录，推荐相似景点
    
    Returns:
        推荐景点列表
    """
    # 获取当前用户ID
    current_user_id = get_jwt_identity()
    
    # 获取查询参数
    limit = request.args.get('limit', default=10, type=int)
    
    # 这里应该查询用户的历史记录，但由于模型中没有定义相关关系
    # 这里使用模拟数据进行演示
    # 在实际应用中，应该基于用户的浏览历史、收藏和评价记录进行推荐
    
    # 随机选择一些景点作为推荐结果
    recommended_places = Place.query.order_by(
        func.random()
    ).limit(limit).all()
    
    # 转换为字典
    result = [place.to_dict() for place in recommended_places]
    
    return jsonify({
        'status': 'success',
        'data': {
            'places': result,
            'count': len(result)
        }
    })

@recommend_bp.route('/places/nearby', methods=['GET'])
@jwt_required(optional=True)
def recommend_nearby_places():
    """基于地理位置的推荐
    
    推荐用户当前位置附近的景点
    
    Args:
        latitude: 纬度
        longitude: 经度
        radius: 搜索半径(公里)，默认5公里
        limit: 返回结果数量限制，默认10个
    
    Returns:
        附近景点列表
    """
    # 获取查询参数
    try:
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        radius = request.args.get('radius', default=5.0, type=float)
        limit = request.args.get('limit', default=10, type=int)
        
        # 验证必要参数
        if latitude is None or longitude is None:
            return jsonify({
                'status': 'error',
                'message': '缺少必要参数：纬度或经度'
            }), 400
        
        # 使用Place模型中的方法获取附近景点
        nearby_places = Place.get_nearby_places(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            limit=limit
        )
        
        # 转换为字典
        result = [place.to_dict() for place in nearby_places]
        
        return jsonify({
            'status': 'success',
            'data': {
                'places': result,
                'count': len(result)
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'获取附近景点失败: {str(e)}'
        }), 500

@recommend_bp.route('/places/ai', methods=['GET'])
@jwt_required()
def ai_recommend_places():
    """AI推荐算法
    
    使用AI算法进行个性化推荐
    
    Returns:
        AI推荐的景点列表
    """
    # 获取当前用户ID
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({
            'status': 'error',
            'message': '用户不存在'
        }), 404
    
    # 获取查询参数
    limit = request.args.get('limit', default=10, type=int)
    
    # 这里应该调用AI推荐模块进行推荐
    # 由于AI推荐模块尚未实现，这里使用随机推荐进行模拟
    # 在实际应用中，应该导入并调用ai_recommendation模块中的算法
    
    # 随机选择一些景点作为推荐结果
    ai_recommended_places = Place.query.order_by(
        func.random()
    ).limit(limit).all()
    
    # 转换为字典
    result = [place.to_dict() for place in ai_recommended_places]
    
    return jsonify({
        'status': 'success',
        'data': {
            'places': result,
            'count': len(result),
            'algorithm': 'AI推荐算法（模拟）'
        }
    })