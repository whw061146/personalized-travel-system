from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Place, Food, Diary, User
from utils.helpers import calculate_similarity

recommend_bp = Blueprint('recommend', __name__)

# 推荐景点、美食、游记
@recommend_bp.route('/places', methods=['GET'])
@jwt_required()
def recommend_places():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    places = Place.query.order_by(Place.rating.desc()).limit(10).all()
    result = [{'id': p.id, 'name': p.name, 'rating': p.rating} for p in places]
    
    return jsonify({'recommended_places': result}), 200

@recommend_bp.route('/foods', methods=['GET'])
@jwt_required()
def recommend_foods():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    foods = Food.query.order_by(Food.rating.desc()).limit(10).all()
    result = [{'id': f.id, 'name': f.name, 'rating': f.rating} for f in foods]
    
    return jsonify({'recommended_foods': result}), 200

@recommend_bp.route('/diaries', methods=['GET'])
@jwt_required()
def recommend_diaries():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    diaries = Diary.query.order_by(Diary.rating.desc()).limit(10).all()
    result = [{'id': d.id, 'title': d.title, 'rating': d.rating} for d in diaries]
    
    return jsonify({'recommended_diaries': result}), 200
