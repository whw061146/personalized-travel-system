import os
import datetime

class Config:
    """基础配置类"""
    # 应用配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-please-change-in-production')
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:password@localhost/travel_system')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-please-change')
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=1)  # 令牌过期时间：1天
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 最大上传文件大小：16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False
    # 开发环境可以使用SQLite简化配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///dev.db')
    # 开发环境下的JWT令牌过期时间可以设置长一些，方便调试
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=7)

class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = False
    TESTING = True
    # 测试环境使用内存数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # 测试环境下禁用CSRF保护
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    # 生产环境必须通过环境变量设置密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'production-key-please-change'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-production-key-please-change'
    # 生产环境下的数据库URI必须通过环境变量设置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # 生产环境下的JWT令牌过期时间设置短一些，增强安全性
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=12)
    # 启用HTTPS
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True