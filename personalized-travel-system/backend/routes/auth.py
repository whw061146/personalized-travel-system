from flask import Blueprint, request, jsonify
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timedelta
import re

# 创建 Blueprint
auth_bp = Blueprint('auth', __name__)

# 邮箱格式验证
def is_valid_email(email):
    pattern = r'^[\w\.-]+@([\w\-]+\.)+[A-Za-z]{2,}$'
    return re.match(pattern, email) is not None

# 密码强度验证
def is_strong_password(password):
    # 至少8个字符，包含大小写字母和数字
    if len(password) < 8:
        return False, "密码长度至少为8个字符"
    if not re.search(r'[A-Z]', password):
        return False, "密码必须包含至少一个大写字母"
    if not re.search(r'[a-z]', password):
        return False, "密码必须包含至少一个小写字母"
    if not re.search(r'\d', password):
        return False, "密码必须包含至少一个数字"
    return True, ""

# 用户注册
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    avatar_url = data.get('avatar_url')
    
    if not username or not email or not password:
        return jsonify({'error': '缺少必要参数'}), 400
    
    # 验证邮箱格式
    if not is_valid_email(email):
        return jsonify({'error': '邮箱格式不正确'}), 400
    
    # 验证密码强度
    is_valid, error_msg = is_strong_password(password)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    # 检查用户是否已存在
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': '用户已存在'}), 409
    
    # 哈希加密密码
    hashed_password = generate_password_hash(password)
    
    try:
        # 创建新用户
        new_user = User(username=username, email=email, password_hash=hashed_password, avatar_url=avatar_url)
        db.session.add(new_user)
        db.session.commit()
        
        # 生成JWT令牌
        access_token = create_access_token(identity=new_user.id)
        
        return jsonify({
            'message': '注册成功',
            'access_token': access_token,
            'user': new_user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'注册失败: {str(e)}'}), 500

# 用户登录
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': '缺少必要参数'}), 400
    
    try:
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'error': '邮箱或密码错误'}), 401
        
        # 生成 JWT 令牌，有效期1小时
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=1)
        )
        
        return jsonify({
            'access_token': access_token, 
            'message': '登录成功',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': f'登录失败: {str(e)}'}), 500

# 获取用户信息
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': f'获取用户信息失败: {str(e)}'}), 500

# 更新用户信息
@auth_bp.route('/update', methods=['PUT'])
@jwt_required()
def update_user():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 更新用户名
        if 'username' in data:
            user.username = data['username']
        
        # 更新头像
        if 'avatar_url' in data:
            user.avatar_url = data['avatar_url']
        
        # 更新偏好
        if 'preferences' in data:
            user.preferences = data['preferences']
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': '用户信息更新成功',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新用户信息失败: {str(e)}'}), 500

# 修改密码
@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'error': '缺少必要参数'}), 400
    
    # 验证新密码强度
    is_valid, error_msg = is_strong_password(new_password)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 验证当前密码
        if not check_password_hash(user.password_hash, current_password):
            return jsonify({'error': '当前密码错误'}), 401
        
        # 更新密码
        user.password_hash = generate_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': '密码修改成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'修改密码失败: {str(e)}'}), 500

# 注销账户
@auth_bp.route('/delete-account', methods=['DELETE'])
@jwt_required()
def delete_account():
    user_id = get_jwt_identity()
    data = request.get_json()
    password = data.get('password')
    
    if not password:
        return jsonify({'error': '请提供密码以确认账户删除'}), 400
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 验证密码
        if not check_password_hash(user.password_hash, password):
            return jsonify({'error': '密码错误，无法删除账户'}), 401
        
        # 删除用户
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': '账户已成功注销'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'注销账户失败: {str(e)}'}), 500

# 刷新令牌
@auth_bp.route('/refresh-token', methods=['POST'])
@jwt_required()
def refresh_token():
    user_id = get_jwt_identity()
    try:
        # 检查用户是否存在
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 生成新的访问令牌
        new_token = create_access_token(
            identity=user_id,
            expires_delta=timedelta(hours=1)
        )
        
        return jsonify({
            'access_token': new_token,
            'message': '令牌刷新成功'
        }), 200
    except Exception as e:
        return jsonify({'error': f'刷新令牌失败: {str(e)}'}), 500
