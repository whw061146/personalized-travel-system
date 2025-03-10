import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from backend.models import db  # ✅ 确保 models/__init__.py 里已初始化 db
from backend.routes import total_bp  # ✅ 统一 Blueprint 入口

# 初始化 Flask 应用
app = Flask(__name__)

# 数据库配置
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://user:password@localhost/travel_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "your_secret_key_here"

# 绑定数据库（✅ 这里不会重复初始化）
db.init_app(app)

# 其他 Flask 插件
CORS(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# 注册 API 路由
app.register_blueprint(total_bp)

# **⚠️ 移除 db = SQLAlchemy(app)**
# 这里已经通过 `models/__init__.py` 里 `db = SQLAlchemy()` 进行了初始化，不需要再次创建

# **🚀 确保数据库表只创建一次**
with app.app_context():
    db.create_all()

# 运行 Flask 服务器
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
