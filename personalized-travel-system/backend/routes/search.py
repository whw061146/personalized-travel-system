from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, func

# 导入数据库和模型
from models import db
from models.place import Place
from models.food import Food

# 创建搜索蓝图
search_bp = Blueprint('search', __name__)

@search_bp.route('/all', methods=['GET'])
def search_all():
    """全文搜索API
    
    搜索景点和美食信息
    
    Query Parameters:
        q: 搜索关键词
        type: 搜索类型 (all, place, food)
        city: 城市筛选
        min_rating: 最低评分
        max_rating: 最高评分
        sort_by: 排序字段 (rating, popularity, name)
        sort_order: 排序方式 (asc, desc)
        limit: 返回结果数量限制
        offset: 分页偏移量
    
    Returns:
        搜索结果列表
    """
    # 获取查询参数
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'all')
    city = request.args.get('city')
    min_rating = request.args.get('min_rating', type=float)
    max_rating = request.args.get('max_rating', type=float)
    sort_by = request.args.get('sort_by', 'rating')
    sort_order = request.args.get('sort_order', 'desc')
    limit = request.args.get('limit', default=20, type=int)
    offset = request.args.get('offset', default=0, type=int)
    
    # 验证参数
    if sort_by not in ['rating', 'popularity', 'name']:
        sort_by = 'rating'
    
    if sort_order not in ['asc', 'desc']:
        sort_order = 'desc'
    
    # 初始化结果
    results = {
        'places': [],
        'foods': [],
        'total_count': 0
    }
    
    # 搜索景点
    if search_type in ['all', 'place']:
        places_query = Place.query
        
        # 关键词搜索
        if query:
            places_query = places_query.filter(
                or_(
                    Place.name.ilike(f'%{query}%'),
                    Place.description.ilike(f'%{query}%'),
                    Place.place_type.ilike(f'%{query}%')
                )
            )
        
        # 城市筛选
        if city:
            places_query = places_query.filter(Place.city == city)
        
        # 评分筛选
        if min_rating is not None:
            places_query = places_query.filter(Place.rating >= min_rating)
        if max_rating is not None:
            places_query = places_query.filter(Place.rating <= max_rating)
        
        # 排序
        if sort_by == 'rating':
            places_query = places_query.order_by(
                Place.rating.desc() if sort_order == 'desc' else Place.rating.asc()
            )
        elif sort_by == 'popularity':
            places_query = places_query.order_by(
                Place.popularity.desc() if sort_order == 'desc' else Place.popularity.asc()
            )
        elif sort_by == 'name':
            places_query = places_query.order_by(
                Place.name.desc() if sort_order == 'desc' else Place.name.asc()
            )
        
        # 获取总数
        places_count = places_query.count()
        
        # 分页
        places = places_query.offset(offset).limit(limit).all()
        
        # 转换为字典
        results['places'] = [place.to_dict() for place in places]
        results['total_count'] += places_count
    
    # 搜索美食
    if search_type in ['all', 'food']:
        foods_query = Food.query
        
        # 关键词搜索
        if query:
            foods_query = foods_query.filter(
                or_(
                    Food.name.ilike(f'%{query}%'),
                    Food.description.ilike(f'%{query}%'),
                    Food.cuisine_type.ilike(f'%{query}%'),
                    Food.restaurant_name.ilike(f'%{query}%')
                )
            )
        
        # 城市筛选
        if city:
            foods_query = foods_query.filter(Food.city == city)
        
        # 评分筛选
        if min_rating is not None:
            foods_query = foods_query.filter(Food.rating >= min_rating)
        if max_rating is not None:
            foods_query = foods_query.filter(Food.rating <= max_rating)
        
        # 排序
        if sort_by == 'rating':
            foods_query = foods_query.order_by(
                Food.rating.desc() if sort_order == 'desc' else Food.rating.asc()
            )
        elif sort_by == 'popularity':
            # 美食模型没有popularity字段，使用review_count代替
            foods_query = foods_query.order_by(
                Food.review_count.desc() if sort_order == 'desc' else Food.review_count.asc()
            )
        elif sort_by == 'name':
            foods_query = foods_query.order_by(
                Food.name.desc() if sort_order == 'desc' else Food.name.asc()
            )
        
        # 获取总数
        foods_count = foods_query.count()
        
        # 分页
        foods = foods_query.offset(offset).limit(limit).all()
        
        # 转换为字典
        results['foods'] = [food.to_dict() for food in foods]
        results['total_count'] += foods_count
    
    return jsonify({
        'status': 'success',
        'data': results
    })

@search_bp.route('/places', methods=['GET'])
def search_places():
    """景点搜索API
    
    按类型、位置、评分等筛选景点
    
    Query Parameters:
        q: 搜索关键词
        place_type: 景点类型
        tags: 标签列表 (逗号分隔)
        city: 城市
        min_rating: 最低评分
        max_rating: 最高评分
        sort_by: 排序字段 (rating, popularity, name)
        sort_order: 排序方式 (asc, desc)
        limit: 返回结果数量限制
        offset: 分页偏移量
    
    Returns:
        景点搜索结果
    """
    # 获取查询参数
    query = request.args.get('q', '')
    place_type = request.args.get('place_type')
    tags_str = request.args.get('tags')
    city = request.args.get('city')
    min_rating = request.args.get('min_rating', type=float)
    max_rating = request.args.get('max_rating', type=float)
    sort_by = request.args.get('sort_by', 'rating')
    sort_order = request.args.get('sort_order', 'desc')
    limit = request.args.get('limit', default=20, type=int)
    offset = request.args.get('offset', default=0, type=int)
    
    # 处理标签
    tags = tags_str.split(',') if tags_str else None
    
    # 构建查询
    places_query = Place.query
    
    # 关键词搜索
    if query:
        places_query = places_query.filter(
            or_(
                Place.name.ilike(f'%{query}%'),
                Place.description.ilike(f'%{query}%')
            )
        )
    
    # 类型筛选
    if place_type:
        places_query = places_query.filter(Place.place_type == place_type)
    
    # 标签筛选
    if tags:
        for tag in tags:
            places_query = places_query.filter(Place.tags.contains([tag]))
    
    # 城市筛选
    if city:
        places_query = places_query.filter(Place.city == city)
    
    # 评分筛选
    if min_rating is not None:
        places_query = places_query.filter(Place.rating >= min_rating)
    if max_rating is not None:
        places_query = places_query.filter(Place.rating <= max_rating)
    
    # 排序
    if sort_by == 'rating':
        places_query = places_query.order_by(
            Place.rating.desc() if sort_order == 'desc' else Place.rating.asc()
        )
    elif sort_by == 'popularity':
        places_query = places_query.order_by(
            Place.popularity.desc() if sort_order == 'desc' else Place.popularity.asc()
        )
    elif sort_by == 'name':
        places_query = places_query.order_by(
            Place.name.desc() if sort_order == 'desc' else Place.name.asc()
        )
    
    # 获取总数
    total_count = places_query.count()
    
    # 分页
    places = places_query.offset(offset).limit(limit).all()
    
    # 转换为字典
    results = [place.to_dict() for place in places]
    
    return jsonify({
        'status': 'success',
        'data': {
            'places': results,
            'total_count': total_count
        }
    })

@search_bp.route('/foods', methods=['GET'])
def search_foods():
    """美食搜索API
    
    按类型、口味、价格等筛选美食
    
    Query Parameters:
        q: 搜索关键词
        cuisine_type: 美食类型
        taste_tags: 口味标签列表 (逗号分隔)
        city: 城市
        price_level: 价格等级 (1-5)
        min_rating: 最低评分
        max_rating: 最高评分
        sort_by: 排序字段 (rating, price_level, name)
        sort_order: 排序方式 (asc, desc)
        limit: 返回结果数量限制
        offset: 分页偏移量
    
    Returns:
        美食搜索结果
    """
    # 获取查询参数
    query = request.args.get('q', '')
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
    foods_query = Food.query
    
    # 关键词搜索
    if query:
        foods_query = foods_query.filter(
            or_(
                Food.name.ilike(f'%{query}%'),
                Food.description.ilike(f'%{query}%'),
                Food.restaurant_name.ilike(f'%{query}%')
            )
        )
    
    # 类型筛选
    if cuisine_type:
        foods_query = foods_query.filter(Food.cuisine_type == cuisine_type)
    
    # 口味标签筛选
    if taste_tags:
        for tag in taste_tags:
            foods_query = foods_query.filter(Food.taste_tags.contains([tag]))
    
    # 城市筛选
    if city:
        foods_query = foods_query.filter(Food.city == city)
    
    # 价格等级筛选
    if price_level is not None:
        foods_query = foods_query.filter(Food.price_level == price_level)
    
    # 评分筛选
    if min_rating is not None:
        foods_query = foods_query.filter(Food.rating >= min_rating)
    if max_rating is not None:
        foods_query = foods_query.filter(Food.rating <= max_rating)
    
    # 排序
    if sort_by == 'rating':
        foods_query = foods_query.order_by(
            Food.rating.desc() if sort_order == 'desc' else Food.rating.asc()
        )
    elif sort_by == 'price_level':
        foods_query = foods_query.order_by(
            Food.price_level.desc() if sort_order == 'desc' else Food.price_level.asc()
        )
    elif sort_by == 'name':
        foods_query = foods_query.order_by(
            Food.name.desc() if sort_order == 'desc' else Food.name.asc()
        )
    
    # 获取总数
    total_count = foods_query.count()
    
    # 分页
    foods = foods_query.offset(offset).limit(limit).all()
    
    # 转换为字典
    results = [food.to_dict() for food in foods]
    
    return jsonify({
        'status': 'success',
        'data': {
            'foods': results,
            'total_count': total_count
        }
    })

@search_bp.route('/suggestions', methods=['GET'])
def search_suggestions():
    """搜索建议API
    
    根据用户输入的关键词提供搜索建议
    
    Query Parameters:
        q: 搜索关键词
        type: 搜索类型 (all, place, food)
        limit: 返回结果数量限制
    
    Returns:
        搜索建议列表
    """
    # 获取查询参数
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'all')
    limit = request.args.get('limit', default=10, type=int)
    
    if not query or len(query) < 2:
        return jsonify({
            'status': 'success',
            'data': {
                'suggestions': []
            }
        })
    
    suggestions = []
    
    # 景点名称建议
    if search_type in ['all', 'place']:
        place_names = db.session.query(Place.name).filter(
            Place.name.ilike(f'%{query}%')
        ).limit(limit).all()
        
        suggestions.extend([name[0] for name in place_names])
    
    # 美食名称建议
    if search_type in ['all', 'food']:
        food_names = db.session.query(Food.name).filter(
            Food.name.ilike(f'%{query}%')
        ).limit(limit).all()
        
        suggestions.extend([name[0] for name in food_names])
    
    # 餐厅名称建议
    if search_type in ['all', 'food']:
        restaurant_names = db.session.query(Food.restaurant_name).filter(
            Food.restaurant_name.ilike(f'%{query}%')
        ).limit(limit).all()
        
        suggestions.extend([name[0] for name in restaurant_names if name[0]])
    
    # 去重并限制数量
    unique_suggestions = list(set(suggestions))[:limit]
    
    return jsonify({
        'status': 'success',
        'data': {
            'suggestions': unique_suggestions
        }
    })