from flask import Blueprint, request, jsonify
from backend.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

# 创建 Blueprint
auth_bp = Blueprint('auth', __name__)

# 用户注册
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({'error': '缺少必要参数'}), 400
    
    # 检查用户是否已存在
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': '用户已存在'}), 409
    
    # 哈希加密密码
    hashed_password = generate_password_hash(password)
    
    # 创建新用户
    new_user = User(username=username, email=email, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': '注册成功'}), 201

# 用户登录
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': '邮箱或密码错误'}), 401
    
    # 生成 JWT 令牌
    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token, 'message': '登录成功'}), 200

# 获取用户信息
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    return jsonify({'id': user.id, 'username': user.username, 'email': user.email}), 200
