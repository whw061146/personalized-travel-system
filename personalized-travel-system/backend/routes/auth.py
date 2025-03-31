from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity, get_jwt
)
from datetime import datetime, timedelta
import re

# 导入数据库和用户模型
from models import db
from models.user import User

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__)

# 邮箱格式验证正则表达式
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
# 密码强度验证正则表达式（至少8位，包含大小写字母和数字）
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$')

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册API"""
    data = request.get_json()
    
    # 验证必要字段
    if not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({
            'status': 'error',
            'message': '缺少必要字段：用户名、邮箱或密码'
        }), 400
    
    # 验证邮箱格式
    if not EMAIL_REGEX.match(data['email']):
        return jsonify({
            'status': 'error',
            'message': '邮箱格式不正确'
        }), 400
    
    # 验证密码强度
    if not PASSWORD_REGEX.match(data['password']):
        return jsonify({
            'status': 'error',
            'message': '密码必须至少8位，包含大小写字母和数字'
        }), 400
    
    # 检查用户名和邮箱是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({
            'status': 'error',
            'message': '用户名已存在'
        }), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({
            'status': 'error',
            'message': '邮箱已被注册'
        }), 409
    
    # 创建新用户
    try:
        user = User(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )
        
        # 处理可选字段
        if 'avatar' in data:
            user.avatar = data['avatar']
        if 'bio' in data:
            user.bio = data['bio']
        if 'travel_preferences' in data:
            user.travel_preferences = data['travel_preferences']
        if 'food_preferences' in data:
            user.food_preferences = data['food_preferences']
        if 'budget_level' in data:
            user.budget_level = data['budget_level']
        if 'transportation_preference' in data:
            user.transportation_preference = data['transportation_preference']
        if 'accommodation_preference' in data:
            user.accommodation_preference = data['accommodation_preference']
        
        # 保存到数据库
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '注册成功',
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'注册失败: {str(e)}'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录API"""
    data = request.get_json()
    
    # 验证必要字段
    if not all(k in data for k in ('email', 'password')):
        return jsonify({
            'status': 'error',
            'message': '缺少必要字段：邮箱或密码'
        }), 400
    
    # 查找用户
    user = User.query.filter_by(email=data['email']).first()
    
    # 验证用户存在且密码正确
    if user and user.check_password(data['password']):
        # 更新最后登录时间
        user.update_last_login()
        
        # 创建访问令牌和刷新令牌
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'status': 'success',
            'message': '登录成功',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200
    
    return jsonify({
        'status': 'error',
        'message': '邮箱或密码错误'
    }), 401

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出API"""
    # JWT本身是无状态的，客户端只需要删除令牌即可
    # 这里可以实现令牌黑名单功能，但需要Redis等存储支持
    # 简化版本只返回成功消息
    return jsonify({
        'status': 'success',
        'message': '登出成功'
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_user_info():
    """获取当前用户信息API"""
    # 获取当前用户ID
    user_id = get_jwt_identity()
    
    # 查找用户
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({
            'status': 'error',
            'message': '用户不存在'
        }), 404
    
    return jsonify({
        'status': 'success',
        'user': user.to_dict()
    }), 200

@auth_bp.route('/update', methods=['PUT'])
@jwt_required()
def update_user_info():
    """更新用户信息API"""
    # 获取当前用户ID
    user_id = get_jwt_identity()
    
    # 查找用户
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({
            'status': 'error',
            'message': '用户不存在'
        }), 404
    
    data = request.get_json()
    
    try:
        # 更新可修改的字段
        if 'username' in data and data['username'] != user.username:
            # 检查新用户名是否已存在
            if User.query.filter_by(username=data['username']).first():
                return jsonify({
                    'status': 'error',
                    'message': '用户名已存在'
                }), 409
            user.username = data['username']
        
        if 'avatar' in data:
            user.avatar = data['avatar']
        if 'bio' in data:
            user.bio = data['bio']
        if 'travel_preferences' in data:
            user.travel_preferences = data['travel_preferences']
        if 'food_preferences' in data:
            user.food_preferences = data['food_preferences']
        if 'budget_level' in data:
            user.budget_level = data['budget_level']
        if 'transportation_preference' in data:
            user.transportation_preference = data['transportation_preference']
        if 'accommodation_preference' in data:
            user.accommodation_preference = data['accommodation_preference']
        
        # 保存到数据库
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '用户信息更新成功',
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'更新失败: {str(e)}'
        }), 500

@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    """修改密码API"""
    # 获取当前用户ID
    user_id = get_jwt_identity()
    
    # 查找用户
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({
            'status': 'error',
            'message': '用户不存在'
        }), 404
    
    data = request.get_json()
    
    # 验证必要字段
    if not all(k in data for k in ('current_password', 'new_password')):
        return jsonify({
            'status': 'error',
            'message': '缺少必要字段：当前密码或新密码'
        }), 400
    
    # 验证当前密码
    if not user.check_password(data['current_password']):
        return jsonify({
            'status': 'error',
            'message': '当前密码错误'
        }), 401
    
    # 验证新密码强度
    if not PASSWORD_REGEX.match(data['new_password']):
        return jsonify({
            'status': 'error',
            'message': '新密码必须至少8位，包含大小写字母和数字'
        }), 400
    
    try:
        # 更新密码
        user.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '密码修改成功'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'密码修改失败: {str(e)}'
        }), 500

@auth_bp.route('/reset-password', methods=['POST'])
def request_password_reset():
    """请求密码重置API"""
    data = request.get_json()
    
    # 验证必要字段
    if 'email' not in data:
        return jsonify({
            'status': 'error',
            'message': '缺少必要字段：邮箱'
        }), 400
    
    # 查找用户
    user = User.query.filter_by(email=data['email']).first()
    
    if not user:
        # 为了安全，不透露用户是否存在
        return jsonify({
            'status': 'success',
            'message': '如果该邮箱已注册，重置密码的邮件已发送'
        }), 200
    
    # 这里应该实现发送重置密码邮件的逻辑
    # 为了简化，这里只返回成功消息
    # 实际应用中，应该生成重置令牌并发送邮件
    
    return jsonify({
        'status': 'success',
        'message': '重置密码的邮件已发送到您的邮箱'
    }), 200

@auth_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    """重置密码API"""
    # 这里应该验证重置令牌并允许用户设置新密码
    # 为了简化，这里只返回成功消息
    # 实际应用中，应该验证令牌，找到对应用户，并更新密码
    
    data = request.get_json()
    
    # 验证必要字段
    if 'new_password' not in data:
        return jsonify({
            'status': 'error',
            'message': '缺少必要字段：新密码'
        }), 400
    
    # 验证新密码强度
    if not PASSWORD_REGEX.match(data['new_password']):
        return jsonify({
            'status': 'error',
            'message': '新密码必须至少8位，包含大小写字母和数字'
        }), 400
    
    # 模拟重置密码成功
    return jsonify({
        'status': 'success',
        'message': '密码重置成功，请使用新密码登录'
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新访问令牌API"""
    # 获取当前用户ID
    user_id = get_jwt_identity()
    
    # 创建新的访问令牌
    access_token = create_access_token(identity=user_id)
    
    return jsonify({
        'status': 'success',
        'access_token': access_token
    }), 200

@auth_bp.route('/delete-account', methods=['DELETE'])
@jwt_required()
def delete_account():
    """注销账户API"""
    # 获取当前用户ID
    user_id = get_jwt_identity()
    
    # 查找用户
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({
            'status': 'error',
            'message': '用户不存在'
        }), 404
    
    data = request.get_json()
    
    # 验证密码
    if 'password' not in data or not user.check_password(data['password']):
        return jsonify({
            'status': 'error',
            'message': '密码错误'
        }), 401
    
    try:
        # 删除用户
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '账户已成功注销'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'账户注销失败: {str(e)}'
        }), 500