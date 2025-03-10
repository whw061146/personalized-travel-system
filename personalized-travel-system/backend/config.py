import os

class Config:
    """
    配置类：用于存储 Flask 应用的配置信息。
    """
    # Flask 基本配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key_here')  # JWT 加密密钥
    DEBUG = os.getenv('DEBUG', True)  # 是否启用调试模式
    
    # 数据库配置（MySQL）
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'your_password_here')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'travel_db')
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 关闭修改跟踪
    
    # JWT 配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key_here')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # Token 过期时间（秒）
    
    # CORS 允许所有来源（仅开发阶段）
    CORS_HEADERS = 'Content-Type'

# 创建配置对象
config = Config()
