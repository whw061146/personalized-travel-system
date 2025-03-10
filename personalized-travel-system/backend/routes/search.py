from flask import Blueprint, request, jsonify
from backend.models import db, Place, Food, Diary

search_bp = Blueprint('search', __name__)

# 通用搜索接口（景点、美食、旅游日记）
@search_bp.route('/places', methods=['GET'])
def search_places():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': '搜索关键词不能为空'}), 400
    
    places = Place.query.filter(Place.name.ilike(f'%{query}%')).all()
    result = [{'id': p.id, 'name': p.name, 'description': p.description, 'rating': p.rating} for p in places]
    
    return jsonify({'search_results': result}), 200

@search_bp.route('/foods', methods=['GET'])
def search_foods():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': '搜索关键词不能为空'}), 400
    
    foods = Food.query.filter(Food.name.ilike(f'%{query}%')).all()
    result = [{'id': f.id, 'name': f.name, 'description': f.description, 'rating': f.rating} for f in foods]
    
    return jsonify({'search_results': result}), 200

@search_bp.route('/diaries', methods=['GET'])
def search_diaries():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': '搜索关键词不能为空'}), 400
    
    diaries = Diary.query.filter(Diary.title.ilike(f'%{query}%')).all()
    result = [{'id': d.id, 'title': d.title, 'content': d.content[:100] + '...', 'rating': d.rating} for d in diaries]
    
    return jsonify({'search_results': result}), 200
