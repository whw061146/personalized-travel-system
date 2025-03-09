from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

# 初始化 Flask 应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# 配置 MySQL 数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:password@localhost/travel_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'

# 初始化数据库
db = SQLAlchemy(app)

# 导入并注册 Blueprints（各模块 API）
from backend.routes.auth import auth_bp
from backend.routes.recommend import recommend_bp
from backend.routes.search import search_bp
from backend.routes.map import map_bp
from backend.routes.diary import diary_bp
from backend.routes.food import food_bp
from backend.routes.indoor import indoor_bp
from backend.routes.aigc import aigc_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(recommend_bp, url_prefix='/recommend')
app.register_blueprint(search_bp, url_prefix='/search')
app.register_blueprint(map_bp, url_prefix='/map')
app.register_blueprint(diary_bp, url_prefix='/diary')
app.register_blueprint(food_bp, url_prefix='/food')
app.register_blueprint(indoor_bp, url_prefix='/indoor')
app.register_blueprint(aigc_bp, url_prefix='/aigc')

# 创建数据库表（仅在首次运行时执行）
with app.app_context():
    db.create_all()

# 运行 Flask 服务器
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
