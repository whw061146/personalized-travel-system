# 导入所有蓝图
from flask import Blueprint
from flask import Flask

# 导入所有路由模块
from .auth import auth_bp
from .recommend import recommend_bp
from .search import search_bp
from .map import map_bp
from .diary import diary_bp
from .food import food_bp
from .indoor import indoor_bp
from .aigc import aigc_bp

def register_blueprints(app: Flask):
    """
    注册所有蓝图到Flask应用
    
    Args:
        app: Flask应用实例
    """
    # 注册认证蓝图
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # 注册推荐蓝图
    app.register_blueprint(recommend_bp, url_prefix='/api/recommend')
    
    # 注册搜索蓝图
    app.register_blueprint(search_bp, url_prefix='/api/search')
    
    # 注册地图蓝图
    app.register_blueprint(map_bp, url_prefix='/api/map')
    
    # 注册日记蓝图
    app.register_blueprint(diary_bp, url_prefix='/api/diary')
    
    # 注册美食蓝图
    app.register_blueprint(food_bp, url_prefix='/api/food')
    
    # 注册室内导航蓝图
    app.register_blueprint(indoor_bp, url_prefix='/api/indoor')
    
    # 注册AI生成内容蓝图
    app.register_blueprint(aigc_bp, url_prefix='/api/aigc')
    
    # 可以在这里添加更多蓝图注册
    
    return app