from flask import request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from functools import wraps
import re
import html
from models.user import User

# 邮箱格式验证正则表达式
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
# 密码强度验证正则表达式（至少8位，包含大小写字母和数字）
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$')
# SQL注入检测正则表达式
SQL_INJECTION_REGEX = re.compile(
    r'(\b(select|insert|update|delete|drop|alter|create|truncate)\b|\b(union|where|from|having)\b|--|\/\*|\*\/|;)',
    re.IGNORECASE
)

# 密码加密和验证
def validate_password_strength(password):
    """
    验证密码强度
    
    Args:
        password: 待验证的密码
        
    Returns:
        (bool, str): 验证结果和错误消息（如果有）
    """
    if not password or len(password) < 8:
        return False, "密码长度必须至少为8位"
    
    if not PASSWORD_REGEX.match(password):
        return False, "密码必须包含大小写字母和数字"
    
    return True, ""

# JWT令牌处理
def admin_required(fn):
    """
    管理员权限检查装饰器
    
    Args:
        fn: 被装饰的函数
        
    Returns:
        装饰后的函数
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_admin:
            return jsonify({
                'status': 'error',
                'message': '需要管理员权限'
            }), 403
        
        return fn(*args, **kwargs)
    
    return wrapper

def active_user_required(fn):
    """
    活跃用户权限检查装饰器
    
    Args:
        fn: 被装饰的函数
        
    Returns:
        装饰后的函数
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_active:
            return jsonify({
                'status': 'error',
                'message': '账户已被禁用'
            }), 403
        
        return fn(*args, **kwargs)
    
    return wrapper

# 防SQL注入和XSS攻击功能
def sanitize_input(text):
    """
    清理输入文本，防止XSS攻击
    
    Args:
        text: 输入文本
        
    Returns:
        清理后的文本
    """
    if not isinstance(text, str):
        return text
    
    # 转义HTML特殊字符
    return html.escape(text)

def check_sql_injection(text):
    """
    检查是否存在SQL注入攻击
    
    Args:
        text: 输入文本
        
    Returns:
        (bool, str): 检查结果和错误消息（如果有）
    """
    if not isinstance(text, str):
        return True, ""
    
    if SQL_INJECTION_REGEX.search(text):
        return False, "检测到潜在的SQL注入攻击"
    
    return True, ""

def validate_email(email):
    """
    验证邮箱格式
    
    Args:
        email: 待验证的邮箱
        
    Returns:
        bool: 验证结果
    """
    if not email:
        return False
    
    return bool(EMAIL_REGEX.match(email))

def secure_headers():
    """
    生成安全的HTTP响应头
    
    Returns:
        dict: 安全的HTTP响应头
    """
    return {
        'Content-Security-Policy': "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline';",
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block'
    }