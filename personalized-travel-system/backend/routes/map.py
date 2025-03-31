from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, jwt_required
from sqlalchemy import func
import requests
import json

# 导入数据库和模型
from models import db
from models.place import Place
from models.food import Food

# 创建地图蓝图
map_bp = Blueprint('map', __name__)

@map_bp.route('/data', methods=['GET'])
@jwt_required(optional=True)
def get_map_data():
    """地图数据获取API
    
    获取指定区域的地图数据，包括景点、餐厅等
    
    Query Parameters:
        latitude: 中心点纬度
        longitude: 中心点经度
        radius: 搜索半径(公里)，默认5公里
        types: 数据类型 (all, place, food, facility)，默认all
        limit: 返回结果数量限制，默认20个
    
    Returns:
        地图数据列表
    """
    # 获取查询参数
    try:
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        radius = request.args.get('radius', default=5.0, type=float)
        data_types = request.args.get('types', default='all')
        limit = request.args.get('limit', default=20, type=int)
        
        # 验证必要参数
        if latitude is None or longitude is None:
            return jsonify({
                'status': 'error',
                'message': '缺少必要参数：纬度或经度'
            }), 400
        
        # 初始化结果
        results = {
            'places': [],
            'foods': [],
            'facilities': [],
            'total_count': 0
        }
        
        # 获取景点数据
        if data_types in ['all', 'place']:
            places = Place.get_nearby_places(
                latitude=latitude,
                longitude=longitude,
                radius=radius,
                limit=limit
            )
            
            # 转换为字典并添加类型标记
            place_results = []
            for place in places:
                place_dict = place.to_dict()
                place_dict['item_type'] = 'place'
                place_results.append(place_dict)
                
            results['places'] = place_results
            results['total_count'] += len(place_results)
        
        # 获取美食数据
        if data_types in ['all', 'food']:
            # 使用Haversine公式计算距离
            earth_radius = 6371.0
            
            # 计算距离并筛选
            distance = func.acos(
                func.sin(func.radians(latitude)) * func.sin(func.radians(Food.latitude)) +
                func.cos(func.radians(latitude)) * func.cos(func.radians(Food.latitude)) *
                func.cos(func.radians(Food.longitude) - func.radians(longitude))
            ) * earth_radius
            
            foods = Food.query.filter(
                distance <= radius
            ).order_by(distance).limit(limit).all()
            
            # 转换为字典并添加类型标记
            food_results = []
            for food in foods:
                food_dict = food.to_dict()
                food_dict['item_type'] = 'food'
                food_results.append(food_dict)
                
            results['foods'] = food_results
            results['total_count'] += len(food_results)
        
        # 获取设施数据（这里需要集成第三方地图服务，暂时返回空列表）
        if data_types in ['all', 'facility']:
            # 在实际应用中，应该调用第三方地图API获取设施数据
            # 例如高德地图、百度地图等
            results['facilities'] = []
        
        return jsonify({
            'status': 'success',
            'data': results
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'获取地图数据失败: {str(e)}'
        }), 500

@map_bp.route('/route', methods=['GET'])
@jwt_required(optional=True)
def plan_route():
    """路径规划功能
    
    规划从起点到终点的最佳路径
    
    Query Parameters:
        start_lat: 起点纬度
        start_lng: 起点经度
        end_lat: 终点纬度
        end_lng: 终点经度
        waypoints: 途经点坐标列表，格式为"lat1,lng1;lat2,lng2"（可选）
        mode: 出行方式 (driving, walking, cycling, transit)，默认driving
    
    Returns:
        规划路径详情
    """
    # 获取查询参数
    try:
        start_lat = request.args.get('start_lat', type=float)
        start_lng = request.args.get('start_lng', type=float)
        end_lat = request.args.get('end_lat', type=float)
        end_lng = request.args.get('end_lng', type=float)
        waypoints_str = request.args.get('waypoints')
        mode = request.args.get('mode', default='driving')
        
        # 验证必要参数
        if None in [start_lat, start_lng, end_lat, end_lng]:
            return jsonify({
                'status': 'error',
                'message': '缺少必要参数：起点或终点坐标'
            }), 400
        
        # 处理途经点
        waypoints = []
        if waypoints_str:
            try:
                waypoint_pairs = waypoints_str.split(';')
                for pair in waypoint_pairs:
                    lat, lng = pair.split(',')
                    waypoints.append({
                        'latitude': float(lat),
                        'longitude': float(lng)
                    })
            except:
                return jsonify({
                    'status': 'error',
                    'message': '途经点格式错误，应为"lat1,lng1;lat2,lng2"'
                }), 400
        
        # 在实际应用中，应该调用第三方地图API进行路径规划
        # 这里使用模拟数据进行演示
        
        # 模拟路径规划结果
        route_result = {
            'distance': 5.2,  # 公里
            'duration': 15,   # 分钟
            'start_address': '起点地址',
            'end_address': '终点地址',
            'steps': [
                {
                    'instruction': '向东行驶100米',
                    'distance': 0.1,
                    'duration': 1
                },
                {
                    'instruction': '右转进入主干道',
                    'distance': 2.5,
                    'duration': 7
                },
                {
                    'instruction': '左转进入目的地',
                    'distance': 2.6,
                    'duration': 7
                }
            ],
            'polyline': '这里是路径的坐标点序列，实际应用中应返回编码后的坐标序列'
        }
        
        return jsonify({
            'status': 'success',
            'data': {
                'route': route_result,
                'mode': mode
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'路径规划失败: {str(e)}'
        }), 500

@map_bp.route('/facilities', methods=['GET'])
def nearby_facilities():
    """附近设施查询
    
    查询指定位置附近的设施
    
    Query Parameters:
        latitude: 中心点纬度
        longitude: 中心点经度
        radius: 搜索半径(公里)，默认1公里
        type: 设施类型 (restaurant, hotel, hospital, bank, gas_station, etc.)
        limit: 返回结果数量限制，默认10个
    
    Returns:
        附近设施列表
    """
    # 获取查询参数
    try:
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        radius = request.args.get('radius', default=1.0, type=float)
        facility_type = request.args.get('type', default='restaurant')
        limit = request.args.get('limit', default=10, type=int)
        
        # 验证必要参数
        if latitude is None or longitude is None:
            return jsonify({
                'status': 'error',
                'message': '缺少必要参数：纬度或经度'
            }), 400
        
        # 在实际应用中，应该调用第三方地图API获取附近设施
        # 这里使用模拟数据进行演示
        
        # 模拟设施数据
        facilities = [
            {
                'id': 1,
                'name': f'{facility_type}示例1',
                'type': facility_type,
                'latitude': latitude + 0.01,
                'longitude': longitude + 0.01,
                'distance': 0.5,  # 公里
                'address': '示例地址1',
                'rating': 4.5,
                'opening_hours': '09:00-22:00'
            },
            {
                'id': 2,
                'name': f'{facility_type}示例2',
                'type': facility_type,
                'latitude': latitude - 0.01,
                'longitude': longitude - 0.01,
                'distance': 0.8,  # 公里
                'address': '示例地址2',
                'rating': 4.2,
                'opening_hours': '08:00-21:00'
            }
        ]
        
        return jsonify({
            'status': 'success',
            'data': {
                'facilities': facilities,
                'count': len(facilities)
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'查询附近设施失败: {str(e)}'
        }), 500

@map_bp.route('/third-party', methods=['GET'])
@jwt_required()
def third_party_map_service():
    """集成第三方地图服务
    
    调用第三方地图API获取特定功能
    
    Query Parameters:
        service: 服务类型 (geocode, weather, traffic, etc.)
        params: 服务参数，JSON格式字符串
    
    Returns:
        第三方服务返回结果
    """
    # 获取查询参数
    try:
        service = request.args.get('service')
        params_str = request.args.get('params', '{}')
        
        # 验证必要参数
        if not service:
            return jsonify({
                'status': 'error',
                'message': '缺少必要参数：服务类型'
            }), 400
        
        # 解析参数
        try:
            params = json.loads(params_str)
        except json.JSONDecodeError:
            return jsonify({
                'status': 'error',
                'message': '参数格式错误，应为有效的JSON字符串'
            }), 400
        
        # 在实际应用中，应该根据service类型调用不同的第三方API
        # 这里使用模拟数据进行演示
        
        # 模拟第三方服务响应
        if service == 'geocode':
            result = {
                'address': '示例地址',
                'latitude': 39.9042,
                'longitude': 116.4074
            }
        elif service == 'weather':
            result = {
                'temperature': 25,
                'weather': '晴',
                'wind': '东北风3级',
                'humidity': '65%'
            }
        elif service == 'traffic':
            result = {
                'status': '畅通',
                'congestion_level': 0.3,
                'incidents': []
            }
        else:
            return jsonify({
                'status': 'error',
                'message': f'不支持的服务类型: {service}'
            }), 400
        
        return jsonify({
            'status': 'success',
            'data': {
                'service': service,
                'result': result
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'调用第三方地图服务失败: {str(e)}'
        }), 500