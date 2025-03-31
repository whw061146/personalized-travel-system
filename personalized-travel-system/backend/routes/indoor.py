from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
import json

# 导入数据库和模型
from models import db
from models.place import Place
from models.path import Path

# 创建室内导航蓝图
indoor_bp = Blueprint('indoor', __name__)

@indoor_bp.route('/map', methods=['GET'])
@jwt_required(optional=True)
def get_indoor_map():
    """室内地图数据获取API
    
    获取指定建筑物的室内地图数据
    
    Query Parameters:
        building_id: 建筑物ID
        floor: 楼层，默认1楼
    
    Returns:
        室内地图数据
    """
    # 获取查询参数
    try:
        building_id = request.args.get('building_id', type=int)
        floor = request.args.get('floor', default=1, type=int)
        
        # 验证必要参数
        if building_id is None:
            return jsonify({
                'status': 'error',
                'message': '缺少必要参数：建筑物ID'
            }), 400
        
        # 在实际应用中，应该从数据库获取室内地图数据
        # 这里使用模拟数据进行演示
        
        # 模拟室内地图数据
        indoor_map_data = {
            'building_id': building_id,
            'building_name': f'示例建筑 {building_id}',
            'floor': floor,
            'floor_name': f'{floor}楼',
            'width': 100,  # 地图宽度（米）
            'height': 80,  # 地图高度（米）
            'elements': [
                {
                    'id': 1,
                    'type': 'room',
                    'name': '101会议室',
                    'x': 10,
                    'y': 20,
                    'width': 15,
                    'height': 10
                },
                {
                    'id': 2,
                    'type': 'corridor',
                    'name': '走廊',
                    'points': [[0, 25], [100, 25], [100, 30], [0, 30]]
                },
                {
                    'id': 3,
                    'type': 'elevator',
                    'name': '电梯',
                    'x': 50,
                    'y': 40,
                    'width': 5,
                    'height': 5
                },
                {
                    'id': 4,
                    'type': 'stairs',
                    'name': '楼梯',
                    'x': 60,
                    'y': 40,
                    'width': 8,
                    'height': 5
                },
                {
                    'id': 5,
                    'type': 'facility',
                    'name': '洗手间',
                    'x': 70,
                    'y': 20,
                    'width': 10,
                    'height': 8
                }
            ]
        }
        
        return jsonify({
            'status': 'success',
            'data': indoor_map_data
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'获取室内地图数据失败: {str(e)}'
        }), 500

@indoor_bp.route('/route', methods=['GET'])
@jwt_required(optional=True)
def plan_indoor_route():
    """室内路径规划API
    
    规划室内从起点到终点的最佳路径
    
    Query Parameters:
        building_id: 建筑物ID
        floor: 楼层
        start_x: 起点X坐标
        start_y: 起点Y坐标
        end_x: 终点X坐标
        end_y: 终点Y坐标
        avoid_stairs: 是否避开楼梯，默认false
        accessibility: 是否考虑无障碍通道，默认false
    
    Returns:
        规划路径详情
    """
    # 获取查询参数
    try:
        building_id = request.args.get('building_id', type=int)
        floor = request.args.get('floor', default=1, type=int)
        start_x = request.args.get('start_x', type=float)
        start_y = request.args.get('start_y', type=float)
        end_x = request.args.get('end_x', type=float)
        end_y = request.args.get('end_y', type=float)
        avoid_stairs = request.args.get('avoid_stairs', default='false') == 'true'
        accessibility = request.args.get('accessibility', default='false') == 'true'
        
        # 验证必要参数
        if None in [building_id, start_x, start_y, end_x, end_y]:
            return jsonify({
                'status': 'error',
                'message': '缺少必要参数：建筑物ID或起终点坐标'
            }), 400
        
        # 在实际应用中，应该使用路径规划算法计算最佳路径
        # 这里使用模拟数据进行演示
        
        # 模拟路径规划结果
        route_result = {
            'distance': 45.5,  # 米
            'duration': 60,    # 秒
            'start_point': {
                'x': start_x,
                'y': start_y,
                'name': '当前位置'
            },
            'end_point': {
                'x': end_x,
                'y': end_y,
                'name': '目的地'
            },
            'path_points': [
                {'x': start_x, 'y': start_y},
                {'x': start_x, 'y': 25},  # 连接到走廊
                {'x': end_x, 'y': 25},    # 沿走廊移动
                {'x': end_x, 'y': end_y}   # 到达目的地
            ],
            'instructions': [
                '从当前位置出发',
                '向北走10米到达走廊',
                '沿走廊向东走30米',
                '向南走5.5米到达目的地'
            ],
            'avoid_stairs': avoid_stairs,
            'accessibility': accessibility
        }
        
        return jsonify({
            'status': 'success',
            'data': {
                'route': route_result,
                'building_id': building_id,
                'floor': floor
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'室内路径规划失败: {str(e)}'
        }), 500

@indoor_bp.route('/facilities', methods=['GET'])
@jwt_required(optional=True)
def get_indoor_facilities():
    """室内设施查询API
    
    查询室内设施信息
    
    Query Parameters:
        building_id: 建筑物ID
        floor: 楼层，默认全部楼层
        facility_type: 设施类型 (restroom, elevator, exit, shop, restaurant, etc)
        nearest: 是否只返回最近的设施，默认false
        current_x: 当前X坐标（与nearest=true一起使用）
        current_y: 当前Y坐标（与nearest=true一起使用）
    
    Returns:
        设施列表
    """
    # 获取查询参数
    try:
        building_id = request.args.get('building_id', type=int)
        floor = request.args.get('floor', type=int)
        facility_type = request.args.get('facility_type')
        nearest = request.args.get('nearest', default='false') == 'true'
        current_x = request.args.get('current_x', type=float)
        current_y = request.args.get('current_y', type=float)
        
        # 验证必要参数
        if building_id is None:
            return jsonify({
                'status': 'error',
                'message': '缺少必要参数：建筑物ID'
            }), 400
        
        if nearest and (current_x is None or current_y is None):
            return jsonify({
                'status': 'error',
                'message': '查询最近设施时，需要提供当前坐标'
            }), 400
        
        # 在实际应用中，应该从数据库查询设施信息
        # 这里使用模拟数据进行演示
        
        # 模拟设施数据
        facilities = [
            {
                'id': 1,
                'name': '男洗手间',
                'type': 'restroom',
                'subtype': 'male',
                'floor': 1,
                'x': 70,
                'y': 20,
                'icon': 'restroom_male_icon.png'
            },
            {
                'id': 2,
                'name': '女洗手间',
                'type': 'restroom',
                'subtype': 'female',
                'floor': 1,
                'x': 70,
                'y': 30,
                'icon': 'restroom_female_icon.png'
            },
            {
                'id': 3,
                'name': '电梯',
                'type': 'elevator',
                'floor': 1,
                'x': 50,
                'y': 40,
                'icon': 'elevator_icon.png'
            },
            {
                'id': 4,
                'name': '紧急出口',
                'type': 'exit',
                'subtype': 'emergency',
                'floor': 1,
                'x': 90,
                'y': 50,
                'icon': 'emergency_exit_icon.png'
            },
            {
                'id': 5,
                'name': '咖啡厅',
                'type': 'restaurant',
                'subtype': 'cafe',
                'floor': 1,
                'x': 30,
                'y': 60,
                'icon': 'cafe_icon.png',
                'opening_hours': '08:00-20:00'
            }
        ]
        
        # 应用筛选条件
        filtered_facilities = facilities
        
        # 按楼层筛选
        if floor is not None:
            filtered_facilities = [f for f in filtered_facilities if f['floor'] == floor]
        
        # 按类型筛选
        if facility_type:
            filtered_facilities = [f for f in filtered_facilities if f['type'] == facility_type]
        
        # 查找最近的设施
        if nearest and current_x is not None and current_y is not None:
            # 计算每个设施到当前位置的距离
            for facility in filtered_facilities:
                dx = facility['x'] - current_x
                dy = facility['y'] - current_y
                facility['distance'] = (dx**2 + dy**2)**0.5  # 欧几里得距离
            
            # 按距离排序
            filtered_facilities.sort(key=lambda f: f['distance'])
            
            # 只返回最近的一个
            if filtered_facilities:
                filtered_facilities = [filtered_facilities[0]]
        
        return jsonify({
            'status': 'success',
            'data': {
                'facilities': filtered_facilities,
                'count': len(filtered_facilities),
                'building_id': building_id
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'查询室内设施失败: {str(e)}'
        }), 500

@indoor_bp.route('/buildings', methods=['GET'])
def get_buildings():
    """获取支持室内导航的建筑物列表
    
    Query Parameters:
        city: 城市名称
        latitude: 纬度（用于查找附近建筑物）
        longitude: 经度（用于查找附近建筑物）
        radius: 搜索半径(公里)，默认5公里
        limit: 返回结果数量限制，默认20个
    
    Returns:
        建筑物列表
    """
    # 获取查询参数
    try:
        city = request.args.get('city')
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        radius = request.args.get('radius', default=5.0, type=float)
        limit = request.args.get('limit', default=20, type=int)
        
        # 在实际应用中，应该从数据库查询建筑物信息
        # 这里使用模拟数据进行演示
        
        # 模拟建筑物数据
        buildings = [
            {
                'id': 1,
                'name': '示例购物中心',
                'type': 'shopping_mall',
                'address': '示例市中心区示例路123号',
                'city': '示例市',
                'latitude': 39.9087,
                'longitude': 116.3975,
                'floors': 5,
                'has_parking': True,
                'opening_hours': '10:00-22:00',
                'description': '大型购物中心，包含各类商店、餐厅和娱乐设施',
                'image': 'mall_image.jpg'
            },
            {
                'id': 2,
                'name': '示例博物馆',
                'type': 'museum',
                'address': '示例市文化区博物馆路45号',
                'city': '示例市',
                'latitude': 39.9127,
                'longitude': 116.4095,
                'floors': 3,
                'has_parking': True,
                'opening_hours': '09:00-17:00',
                'description': '历史博物馆，展示各类文物和艺术品',
                'image': 'museum_image.jpg'
            },
            {
                'id': 3,
                'name': '示例火车站',
                'type': 'train_station',
                'address': '示例市交通区站前路1号',
                'city': '示例市',
                'latitude': 39.9007,
                'longitude': 116.4275,
                'floors': 2,
                'has_parking': True,
                'opening_hours': '05:00-23:00',
                'description': '主要火车站，连接多条铁路线',
                'image': 'station_image.jpg'
            }
        ]
        
        # 应用筛选条件
        filtered_buildings = buildings
        
        # 按城市筛选
        if city:
            filtered_buildings = [b for b in filtered_buildings if b['city'] == city]
        
        # 按位置筛选（查找附近建筑物）
        if latitude is not None and longitude is not None:
            # 计算每个建筑物到当前位置的距离
            for building in filtered_buildings:
                # 使用简化的距离计算（实际应用中应使用Haversine公式）
                dlat = building['latitude'] - latitude
                dlng = building['longitude'] - longitude
                # 简化计算，仅用于演示
                building['distance'] = ((dlat**2 + dlng**2)**0.5) * 111  # 粗略转换为公里
            
            # 筛选在半径范围内的建筑物
            filtered_buildings = [b for b in filtered_buildings if b.get('distance', float('inf')) <= radius]
            
            # 按距离排序
            filtered_buildings.sort(key=lambda b: b.get('distance', float('inf')))
        
        # 限制返回数量
        filtered_buildings = filtered_buildings[:limit]
        
        return jsonify({
            'status': 'success',
            'data': {
                'buildings': filtered_buildings,
                'count': len(filtered_buildings)
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'获取建筑物列表失败: {str(e)}'
        }), 500