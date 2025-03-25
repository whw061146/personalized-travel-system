import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from models import db  # 导入数据库实例
from routes import total_bp  # 导入统一的Blueprint入口
from config import config  # 导入配置

# 初始化 Flask 应用
app = Flask(__name__)

# 加载配置
app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.SQLALCHEMY_TRACK_MODIFICATIONS
app.config["SECRET_KEY"] = config.SECRET_KEY
app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
app.config["DEBUG"] = config.DEBUG

# 初始化数据库
db.init_app(app)

# 初始化其他Flask插件
CORS(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# 注册API蓝图
app.register_blueprint(total_bp)

# 创建数据库表
with app.app_context():
    db.create_all()

# 运行Flask服务器
if __name__ == "__main__":
    app.run(debug=config.DEBUG, host="0.0.0.0", port=5000)
