from flask import Blueprint

# 创建 Blueprint 对象
total_bp = Blueprint("total", __name__)

# 导入各个模块并注册 Blueprint
from .auth import auth_bp
from .recommend import recommend_bp
from .search import search_bp
from .map import map_bp
from .diary import diary_bp
from .food import food_bp
from .indoor import indoor_bp
from .aigc import aigc_bp

# 统一注册路由
total_bp.register_blueprint(auth_bp, url_prefix="/auth")
total_bp.register_blueprint(recommend_bp, url_prefix="/recommend")
total_bp.register_blueprint(search_bp, url_prefix="/search")
total_bp.register_blueprint(map_bp, url_prefix="/map")
total_bp.register_blueprint(diary_bp, url_prefix="/diary")
total_bp.register_blueprint(food_bp, url_prefix="/food")
total_bp.register_blueprint(indoor_bp, url_prefix="/indoor")
total_bp.register_blueprint(aigc_bp, url_prefix="/aigc")
