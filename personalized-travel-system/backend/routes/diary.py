from flask import Blueprint, request, jsonify, current_app, url_for, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime

# 导入数据库和模型
from models import db
from models.diary import Diary
from models.user import User

# 创建日记蓝图
diary_bp = Blueprint('diary', __name__)

# 允许的图片扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@diary_bp.route('/', methods=['GET'])
def get_public_diaries():
    """获取公开的旅游日记列表
    
    Query Parameters:
        limit: 返回结果数量限制
        offset: 分页偏移量
        sort_by: 排序字段 (created_at, updated_at, view_count, like_count)
        sort_order: 排序方式 (asc, desc)
        city: 按城市筛选
        country: 按国家筛选
        tag: 按标签筛选
    
    Returns:
        公开日记列表
    """
    # 获取查询参数
    limit = request.args.get('limit', default=10, type=int)
    offset = request.args.get('offset', default=0, type=int)
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    city = request.args.get('city')
    country = request.args.get('country')
    tag = request.args.get('tag')
    
    # 验证参数
    if sort_by not in ['created_at', 'updated_at', 'view_count', 'like_count']:
        sort_by = 'created_at'
    
    if sort_order not in ['asc', 'desc']:
        sort_order = 'desc'
    
    # 构建查询
    query = Diary.query.filter_by(is_public=True)
    
    # 应用筛选条件
    if city:
        query = query.filter_by(city=city)
    
    if country:
        query = query.filter_by(country=country)
    
    if tag:
        query = query.filter(Diary.tags.contains([tag]))
    
    # 应用排序
    if sort_order == 'desc':
        query = query.order_by(getattr(Diary, sort_by).desc())
    else:
        query = query.order_by(getattr(Diary, sort_by).asc())
    
    # 获取分页结果
    diaries = query.limit(limit).offset(offset).all()
    total = query.count()
    
    # 构建响应
    result = {
        'status': 'success',
        'data': [
            {
                'id': diary.id,
                'title': diary.title,
                'content': diary.content[:200] + '...' if len(diary.content) > 200 else diary.content,
                'location_name': diary.location_name,
                'city': diary.city,
                'country': diary.country,
                'images': diary.images[:1] if diary.images else [],  # 只返回第一张图片
                'created_at': diary.created_at.isoformat(),
                'updated_at': diary.updated_at.isoformat(),
                'view_count': diary.view_count,
                'like_count': diary.like_count,
                'comment_count': diary.comment_count,
                'user_id': diary.user_id,
                'tags': diary.tags
            } for diary in diaries
        ],
        'pagination': {
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_more': offset + limit < total
        }
    }
    
    return jsonify(result)

@diary_bp.route('/my', methods=['GET'])
@jwt_required()
def get_my_diaries():
    """获取当前用户的旅游日记列表
    
    Query Parameters:
        limit: 返回结果数量限制
        offset: 分页偏移量
        sort_by: 排序字段 (created_at, updated_at, view_count, like_count)
        sort_order: 排序方式 (asc, desc)
        is_public: 是否只显示公开日记 (true, false, all)
    
    Returns:
        用户日记列表
    """
    # 获取当前用户ID
    current_user_id = get_jwt_identity()
    
    # 获取查询参数
    limit = request.args.get('limit', default=10, type=int)
    offset = request.args.get('offset', default=0, type=int)
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    is_public = request.args.get('is_public', 'all')
    
    # 验证参数
    if sort_by not in ['created_at', 'updated_at', 'view_count', 'like_count']:
        sort_by = 'created_at'
    
    if sort_order not in ['asc', 'desc']:
        sort_order = 'desc'
    
    # 构建查询
    query = Diary.query.filter_by(user_id=current_user_id)
    
    # 应用公开性筛选
    if is_public == 'true':
        query = query.filter_by(is_public=True)
    elif is_public == 'false':
        query = query.filter_by(is_public=False)
    
    # 应用排序
    if sort_order == 'desc':
        query = query.order_by(getattr(Diary, sort_by).desc())
    else:
        query = query.order_by(getattr(Diary, sort_by).asc())
    
    # 获取分页结果
    diaries = query.limit(limit).offset(offset).all()
    total = query.count()
    
    # 构建响应
    result = {
        'status': 'success',
        'data': [
            {
                'id': diary.id,
                'title': diary.title,
                'content': diary.content,
                'location_name': diary.location_name,
                'latitude': diary.latitude,
                'longitude': diary.longitude,
                'address': diary.address,
                'city': diary.city,
                'province': diary.province,
                'country': diary.country,
                'images': diary.images,
                'is_public': diary.is_public,
                'allow_comments': diary.allow_comments,
                'created_at': diary.created_at.isoformat(),
                'updated_at': diary.updated_at.isoformat(),
                'view_count': diary.view_count,
                'like_count': diary.like_count,
                'comment_count': diary.comment_count,
                'tags': diary.tags
            } for diary in diaries
        ],
        'pagination': {
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_more': offset + limit < total
        }
    }
    
    return jsonify(result)

@diary_bp.route('/<int:diary_id>', methods=['GET'])
def get_diary(diary_id):
    """获取单个旅游日记详情
    
    Args:
        diary_id: 日记ID
    
    Returns:
        日记详情
    """
    diary = Diary.query.get_or_404(diary_id)
    
    # 检查日记是否公开或者是当前用户的日记
    current_user_id = None
    try:
        current_user_id = get_jwt_identity()
    except:
        pass
    
    if not diary.is_public and (not current_user_id or diary.user_id != current_user_id):
        return jsonify({
            'status': 'error',
            'message': '您没有权限查看此日记'
        }), 403
    
    # 增加浏览次数
    diary.view_count += 1
    db.session.commit()
    
    # 获取作者信息
    user = User.query.get(diary.user_id)
    
    # 构建响应
    result = {
        'status': 'success',
        'data': {
            'id': diary.id,
            'title': diary.title,
            'content': diary.content,
            'location_name': diary.location_name,
            'latitude': diary.latitude,
            'longitude': diary.longitude,
            'address': diary.address,
            'city': diary.city,
            'province': diary.province,
            'country': diary.country,
            'images': diary.images,
            'is_public': diary.is_public,
            'allow_comments': diary.allow_comments,
            'created_at': diary.created_at.isoformat(),
            'updated_at': diary.updated_at.isoformat(),
            'view_count': diary.view_count,
            'like_count': diary.like_count,
            'comment_count': diary.comment_count,
            'user_id': diary.user_id,
            'username': user.username if user else None,
            'tags': diary.tags
        }
    }
    
    return jsonify(result)

@diary_bp.route('/', methods=['POST'])
@jwt_required()
def create_diary():
    """创建新的旅游日记
    
    Request Body:
        title: 日记标题
        content: 日记内容
        location_name: 位置名称
        latitude: 纬度
        longitude: 经度
        address: 详细地址
        city: 城市
        province: 省份
        country: 国家
        is_public: 是否公开
        allow_comments: 是否允许评论
        tags: 标签列表
    
    Returns:
        创建的日记ID
    """
    # 获取当前用户ID
    current_user_id = get_jwt_identity()
    
    # 获取请求数据
    data = request.get_json()
    
    # 验证必要字段
    if not all(k in data for k in ('title', 'content')):
        return jsonify({
            'status': 'error',
            'message': '缺少必要字段：标题或内容'
        }), 400
    
    # 创建新日记
    new_diary = Diary(
        title=data['title'],
        content=data['content'],
        user_id=current_user_id,
        location_name=data.get('location_name'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        address=data.get('address'),
        city=data.get('city'),
        province=data.get('province'),
        country=data.get('country'),
        is_public=data.get('is_public', True),
        allow_comments=data.get('allow_comments', True),
        tags=data.get('tags', [])
    )
    
    # 保存到数据库
    db.session.add(new_diary)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '日记创建成功',
        'data': {
            'id': new_diary.id
        }
    }), 201

@diary_bp.route('/<int:diary_id>', methods=['PUT'])
@jwt_required()
def update_diary(diary_id):
    """更新旅游日记
    
    Args:
        diary_id: 日记ID
    
    Request Body:
        title: 日记标题
        content: 日记内容
        location_name: 位置名称
        latitude: 纬度
        longitude: 经度
        address: 详细地址
        city: 城市
        province: 省份
        country: 国家
        is_public: 是否公开
        allow_comments: 是否允许评论
        tags: 标签列表
    
    Returns:
        更新结果
    """
    # 获取当前用户ID
    current_user_id = get_jwt_identity()
    
    # 获取日记
    diary = Diary.query.get_or_404(diary_id)
    
    # 检查权限
    if diary.user_id != current_user_id:
        return jsonify({
            'status': 'error',
            'message': '您没有权限修改此日记'
        }), 403
    
    # 获取请求数据
    data = request.get_json()
    
    # 更新字段
    if 'title' in data:
        diary.title = data['title']
    if 'content' in data:
        diary.content = data['content']
    if 'location_name' in data:
        diary.location_name = data['location_name']
    if 'latitude' in data:
        diary.latitude = data['latitude']
    if 'longitude' in data:
        diary.longitude = data['longitude']
    if 'address' in data:
        diary.address = data['address']
    if 'city' in data:
        diary.city = data['city']
    if 'province' in data:
        diary.province = data['province']
    if 'country' in data:
        diary.country = data['country']
    if 'is_public' in data:
        diary.is_public = data['is_public']
    if 'allow_comments' in data:
        diary.allow_comments = data['allow_comments']
    if 'tags' in data:
        diary.tags = data['tags']
    
    # 更新时间
    diary.updated_at = datetime.utcnow()
    
    # 保存到数据库
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '日记更新成功'
    })

@diary_bp.route('/<int:diary_id>', methods=['DELETE'])
@jwt_required()
def delete_diary(diary_id):
    """删除旅游日记
    
    Args:
        diary_id: 日记ID
    
    Returns:
        删除结果
    """
    # 获取当前用户ID
    current_user_id = get_jwt_identity()
    
    # 获取日记
    diary = Diary.query.get_or_404(diary_id)
    
    # 检查权限
    if diary.user_id != current_user_id:
        return jsonify({
            'status': 'error',
            'message': '您没有权限删除此日记'
        }), 403
    
    # 从数据库删除
    db.session.delete(diary)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '日记删除成功'
    })

@diary_bp.route('/<int:diary_id>/upload', methods=['POST'])
@jwt_required()
def upload_images(diary_id):
    """上传日记图片
    
    Args:
        diary_id: 日记ID
    
    Request Form:
        images: 图片文件列表
    
    Returns:
        上传结果
    """
    # 获取当前用户ID
    current_user_id = get_jwt_identity()
    
    # 获取日记
    diary = Diary.query.get_or_404(diary_id)
    
    # 检查权限
    if diary.user_id != current_user_id:
        return jsonify({
            'status': 'error',
            'message': '您没有权限为此日记上传图片'
        }), 403
    
    # 检查是否有文件上传
    if 'images' not in request.files:
        return jsonify({
            'status': 'error',
            'message': '没有上传文件'
        }), 400
    
    files = request.files.getlist('images')
    
    # 检查是否有选择文件
    if not files or files[0].filename == '':
        return jsonify({
            'status': 'error',
            'message': '没有选择文件'
        }), 400
    
    # 创建上传目录
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'diary_images')
    os.makedirs(upload_folder, exist_ok=True)
    
    # 处理每个上传的文件
    uploaded_files = []
    for file in files:
        if file and allowed_file(file.filename):
            # 生成安全的文件名
            filename = secure_filename(file.filename)
            # 添加唯一标识符
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            # 保存文件
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)
            
            # 生成访问URL
            file_url = url_for('diary.get_image', filename=unique_filename, _external=True)
            uploaded_files.append(file_url)
    
    # 更新日记的图片列表
    if not diary.images:
        diary.images = []
    diary.images.extend(uploaded_files)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': f'成功上传 {len(uploaded_files)} 张图片',
        'data': {
            'images': uploaded_files
        }
    })

@diary_bp.route('/images/<filename>')
def get_image(filename):
    """获取日记图片
    
    Args:
        filename: 图片文件名
    
    Returns:
        图片文件
    """
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'diary_images')
    return send_from_directory(upload_folder, filename)

@diary_bp.route('/<int:diary_id>/like', methods=['POST'])
@jwt_required()
def like_diary(diary_id):
    """点赞日记
    
    Args:
        diary_id: 日记ID
    
    Returns:
        点赞结果
    """
    # 获取日记
    diary = Diary.query.get_or_404(diary_id)
    
    # 增加点赞数
    diary.like_count += 1
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '点赞成功',
        'data': {
            'like_count': diary.like_count
        }
    })

@diary_bp.route('/<int:diary_id>/unlike', methods=['POST'])
@jwt_required()
def unlike_diary(diary_id):
    """取消点赞日记
    
    Args:
        diary_id: 日记ID
    
    Returns:
        取消点赞结果
    """
    # 获取日记
    diary = Diary.query.get_or_404(diary_id)
    
    # 减少点赞数，但不能小于0
    if diary.like_count > 0:
        diary.like_count -= 1
        db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '取消点赞成功',
        'data': {
            'like_count': diary.like_count
        }
    })