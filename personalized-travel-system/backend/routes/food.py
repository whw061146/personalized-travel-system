from flask import Blueprint, request, jsonify
from backend.models import db, Food

food_bp = Blueprint('food', __name__)

# 获取所有美食列表
@food_bp.route('/foods', methods=['GET'])
def get_foods():
    foods = Food.query.all()
    result = [{'id': f.id, 'name': f.name, 'description': f.description, 'rating': f.rating, 'location': f.location} for f in foods]
    return jsonify({'foods': result}), 200

# 获取单个美食详情
@food_bp.route('/foods/<int:food_id>', methods=['GET'])
def get_food_detail(food_id):
    food = Food.query.get(food_id)
    if not food:
        return jsonify({'error': '美食未找到'}), 404
    return jsonify({'id': food.id, 'name': food.name, 'description': food.description, 'rating': food.rating, 'location': food.location}), 200

# 添加美食信息
@food_bp.route('/foods', methods=['POST'])
def add_food():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    rating = data.get('rating', 0)
    location = data.get('location')
    
    if not name or not location:
        return jsonify({'error': '缺少必要信息'}), 400
    
    new_food = Food(name=name, description=description, rating=rating, location=location)
    db.session.add(new_food)
    db.session.commit()
    
    return jsonify({'message': '美食添加成功', 'food_id': new_food.id}), 201

# 删除美食信息
@food_bp.route('/foods/<int:food_id>', methods=['DELETE'])
def delete_food(food_id):
    food = Food.query.get(food_id)
    if not food:
        return jsonify({'error': '美食未找到'}), 404
    
    db.session.delete(food)
    db.session.commit()
    return jsonify({'message': '美食已删除'}), 200