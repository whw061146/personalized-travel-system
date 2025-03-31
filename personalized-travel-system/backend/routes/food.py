from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

# 导入数据库和模型
from models import db
from models.user import User
from models.food import Food

# 创建美食蓝图
food_bp = Blueprint('food', __name__)

@food_bp.route('/recommend', methods=['GET'])
@jwt_required()
def recommend_foods():
    """美食推荐API
    
    基于用户偏好和历史行为推荐美食
    
    Query Parameters:
        latitude: 纬度
        longitude: 经度
        radius: 搜索半径(公里)，默认5公里
        limit: 返回结果数量限制，默认10个
    
    Returns:
        推荐美食列表
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
    latitude = request.args.get('latitude', type=float)
    longitude = request.args.get('longitude', type=float)
    radius = request.args.get('radius', default=5.0, type=float)
    limit = request.args.get('limit', default=10, type=int)
    
    # 基于用户偏好推荐
    recommended_foods = []
    
    # 如果用户有美食偏好，根据偏好标签匹配美食
    if hasattr(user, 'food_preferences') and user.food_preferences and len(user.food_preferences) > 0:
        # 查找与用户偏好标签匹配的美食
        for preference in user.food_preferences:
            # 在美食标签中查找匹配项
            matching_foods = Food.query.filter(
                Food.cuisine_type == preference or Food.taste_tags.contains([preference])
            ).order_by(Food.rating.desc()).limit(limit).all()
            
            recommended_foods.extend(matching_foods)
    
    # 如果有位置信息，获取附近的美食
    if latitude and longitude:
        nearby_foods = Food.get_nearby_foods(latitude, longitude, radius, limit)
        
        # 添加到推荐列表，避免重复
        for food in nearby_foods:
            if food not in recommended_foods:
                recommended_foods.append(food)
    
    # 如果推荐列表为空或不足，添加评分最高的美食
    if len(recommended_foods) < limit:
        top_rated_foods = Food.query.order_by(
            Food.rating.desc()
        ).limit(limit - len(recommended_foods)).all()
        
        # 添加到推荐列表，避免重复
        for food in top_rated_foods:
            if food not in recommended_foods:
                recommended_foods.append(food)
    
    # 限制返回数量并转换为字典
    result = []
    for food in recommended_foods[:limit]:
        food_dict = {
            'id': food.id,
            'name': food.name,
            'description': food.description,
            'price_level': food.price_level,
            'cuisine_type': food.cuisine_type,
            'taste_tags': food.taste_tags,
            'signature_dishes': food.signature_dishes,
            'restaurant_name': food.restaurant_name,
            'latitude': food.latitude,
            'longitude': food.longitude,
            'address': food.address,
            'city': food.city,
            'rating': food.rating,
            'review_count': food.review_count,
            'average_cost': food.average_cost,
            'images': food.images[:1] if food.images else []  # 只返回第一张图片
        }
        result.append(food_dict)
    
    return jsonify({
        'status': 'success',
        'data': {
            'foods': result,
            'count': len(result)
        }
    })

@food_bp.route('/nearby', methods=['GET'])
def get_nearby_foods():
    """获取附近美食API
    
    Query Parameters:
        latitude: 纬度 (必需)
        longitude: 经度 (必需)
        radius: 搜索半径(公里)，默认5公里
        limit: 返回结果数量限制，默认20个
    
    Returns:
        附近美食列表
    """
    # 获取查询参数
    latitude = request.args.get('latitude', type=float)
    longitude = request.args.get('longitude', type=float)
    radius = request.args.get('radius', default=5.0, type=float)
    limit = request.args.get('limit', default=20, type=int)
    
    # 验证必要参数
    if latitude is None or longitude is None:
        return jsonify({
            'status': 'error',
            'message': '缺少必要参数：纬度或经度'
        }), 400
    
    # 获取附近美食
    nearby_foods = Food.get_nearby_foods(latitude, longitude, radius, limit)
    
    # 转换为字典
    result = []
    for food in nearby_foods:
        food_dict = {
            'id': food.id,
            'name': food.name,
            'description': food.description,
            'price_level': food.price_level,
            'cuisine_type': food.cuisine_type,
            'taste_tags': food.taste_tags,
            'signature_dishes': food.signature_dishes,
            'restaurant_name': food.restaurant_name,
            'latitude': food.latitude,
            'longitude': food.longitude,
            'address': food.address,
            'city': food.city,
            'rating': food.rating,
            'review_count': food.review_count,
            'average_cost': food.average_cost,
            'images': food.images[:1] if food.images else []  # 只返回第一张图片
        }
        result.append(food_dict)
    
    return jsonify({
        'status': 'success',
        'data': {
            'foods': result,
            'count': len(result)
        }
    })

@food_bp.route('/filter', methods=['GET'])
def filter_foods():
    """美食筛选API
    
    按口味、价格等条件筛选美食
    
    Query Parameters:
        cuisine_type: 美食类型 (中餐、西餐、日料等)
        taste_tags: 口味标签 (辣、甜、酸等)，逗号分隔
        city: 城市
        price_level: 价格等级 (1-5)
        min_rating: 最低评分
        max_rating: 最高评分
        sort_by: 排序字段 (rating, review_count, price_level)
        sort_order: 排序方式 (asc, desc)
        limit: 返回结果数量限制
        offset: 分页偏移量
    
    Returns:
        筛选后的美食列表
    """
    # 获取查询参数
    cuisine_type = request.args.get('cuisine_type')
    taste_tags_str = request.args.get('taste_tags')
    city = request.args.get('city')
    price_level = request.args.get('price_level', type=int)
    min_rating = request.args.get('min_rating', type=float)
    max_rating = request.args.get('max_rating', type=float)
    sort_by = request.args.get('sort_by', 'rating')
    sort_order = request.args.get('sort_order', 'desc')
    limit = request.args.get('limit', default=20, type=int)
    offset = request.args.get('offset', default=0, type=int)
    
    # 处理口味标签
    taste_tags = taste_tags_str.split(',') if taste_tags_str else None
    
    # 构建查询
    query = Food.query
    
    # 应用筛选条件
    if cuisine_type:
        query = query.filter(Food.cuisine_type == cuisine_type)
    
    if city:
        query = query.filter(Food.city == city)
    
    if price_level:
        query = query.filter(Food.price_level == price_level)
    
    if min_rating is not None:
        query = query.filter(Food.rating >= min_rating)
    
    if max_rating is not None:
        query = query.filter(Food.rating <= max_rating)
    
    if taste_tags:
        for tag in taste_tags:
            query = query.filter(Food.taste_tags.contains([tag]))
    
    # 应用排序
    if sort_by == 'rating':
        query = query.order_by(
            Food.rating.desc() if sort_order == 'desc' else Food.rating.asc()
        )
    elif sort_by == 'review_count':
        query = query.order_by(
            Food.review_count.desc() if sort_order == 'desc' else Food.review_count.asc()
        )
    elif sort_by == 'price_level':
        query = query.order_by(
            Food.price_level.desc() if sort_order == 'desc' else Food.price_level.asc()
        )
    
    # 获取总数
    total = query.count()
    
    # 分页
    foods = query.offset(offset).limit(limit).all()
    
    # 转换为字典
    result = []
    for food in foods:
        food_dict = {
            'id': food.id,
            'name': food.name,
            'description': food.description,
            'price_level': food.price_level,
            'cuisine_type': food.cuisine_type,
            'taste_tags': food.taste_tags,
            'signature_dishes': food.signature_dishes,
            'restaurant_name': food.restaurant_name,
            'latitude': food.latitude,
            'longitude': food.longitude,
            'address': food.address,
            'city': food.city,
            'rating': food.rating,
            'review_count': food.review_count,
            'average_cost': food.average_cost,
            'images': food.images[:1] if food.images else []  # 只返回第一张图片
        }
        result.append(food_dict)
    
    return jsonify({
        'status': 'success',
        'data': {
            'foods': result,
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_more': offset + limit < total
        }
    })

@food_bp.route('/<int:food_id>', methods=['GET'])
def get_food_detail(food_id):
    """获取美食详情API
    
    Args:
        food_id: 美食ID
    
    Returns:
        美食详细信息
    """
    food = Food.query.get_or_404(food_id)
    
    # 构建响应
    result = {
        'id': food.id,
        'name': food.name,
        'description': food.description,
        'price_level': food.price_level,
        'cuisine_type': food.cuisine_type,
        'taste_tags': food.taste_tags,
        'signature_dishes': food.signature_dishes,
        'restaurant_name': food.restaurant_name,
        'latitude': food.latitude,
        'longitude': food.longitude,
        'address': food.address,
        'city': food.city,
        'province': food.province,
        'country': food.country,
        'opening_hours': food.opening_hours,
        'contact_phone': food.contact_phone,
        'website': food.website,
        'rating': food.rating,
        'review_count': food.review_count,
        'average_cost': food.average_cost,
        'suitable_occasions': food.suitable_occasions,
        'images': food.images,
        'created_at': food.created_at.isoformat(),
        'updated_at': food.updated_at.isoformat()
    }
    
    return jsonify({
        'status': 'success',
        'data': result
    })

@food_bp.route('/<int:food_id>/rate', methods=['POST'])
@jwt_required()
def rate_food(food_id):
    """美食评价和评分API
    
    Args:
        food_id: 美食ID
    
    Request Body:
        rating: 评分 (1-5)
        review: 评价内容
    
    Returns:
        评价结果
    """
    # 获取当前用户ID
    current_user_id = get_jwt_identity()
    
    # 获取美食
    food = Food.query.get_or_404(food_id)
    
    # 获取请求数据
    data = request.get_json()
    
    # 验证评分
    rating = data.get('rating')
    if rating is None or not (1 <= rating <= 5):
        return jsonify({
            'status': 'error',
            'message': '评分必须在1-5之间'
        }), 400
    
    # 更新美食评分
    # 这里简化处理，实际应用中应该创建一个单独的评价模型
    # 并计算平均评分
    old_rating = food.rating or 0
    old_count = food.review_count or 0
    
    # 计算新的平均评分
    new_count = old_count + 1
    new_rating = (old_rating * old_count + rating) / new_count
    
    # 更新美食评分和评价数
    food.rating = new_rating
    food.review_count = new_count
    
    # 保存到数据库
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '评价成功',
        'data': {
            'new_rating': new_rating,
            'review_count': new_count
        }
    })