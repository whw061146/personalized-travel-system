from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import db, Diary

diary_bp = Blueprint('diary', __name__)

# 创建旅游日记
@diary_bp.route('/create', methods=['POST'])
@jwt_required()
def create_diary():
    user_id = get_jwt_identity()
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    image_url = data.get('image_url', '')
    video_url = data.get('video_url', '')
    
    if not title or not content:
        return jsonify({'error': '标题和内容不能为空'}), 400
    
    new_diary = Diary(user_id=user_id, title=title, content=content, image_url=image_url, video_url=video_url)
    db.session.add(new_diary)
    db.session.commit()
    
    return jsonify({'message': '旅游日记创建成功', 'diary_id': new_diary.id}), 201

# 获取所有旅游日记
@diary_bp.route('/all', methods=['GET'])
def get_all_diaries():
    diaries = Diary.query.order_by(Diary.created_at.desc()).all()
    result = [{'id': d.id, 'title': d.title, 'content': d.content[:100] + '...', 'views': d.views, 'rating': d.rating} for d in diaries]
    return jsonify({'diaries': result}), 200

# 获取单个旅游日记详情
@diary_bp.route('/<int:diary_id>', methods=['GET'])
def get_diary(diary_id):
    diary = Diary.query.get(diary_id)
    if not diary:
        return jsonify({'error': '旅游日记不存在'}), 404
    
    diary.views += 1  # 增加浏览量
    db.session.commit()
    
    return jsonify({'id': diary.id, 'title': diary.title, 'content': diary.content, 'views': diary.views, 'rating': diary.rating}), 200

# 评分旅游日记
@diary_bp.route('/rate/<int:diary_id>', methods=['POST'])
@jwt_required()
def rate_diary(diary_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    rating = data.get('rating')
    
    if not 1 <= rating <= 5:
        return jsonify({'error': '评分必须在 1 到 5 之间'}), 400
    
    diary = Diary.query.get(diary_id)
    if not diary:
        return jsonify({'error': '旅游日记不存在'}), 404
    
    diary.rating = (diary.rating + rating) / 2  # 计算新评分
    db.session.commit()
    
    return jsonify({'message': '评分成功', 'new_rating': diary.rating}), 200