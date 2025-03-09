from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

# ��ʼ�� Flask Ӧ��
app = Flask(__name__)
CORS(app)  # �����������
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# ���� MySQL ���ݿ�
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:password@localhost/travel_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'

# ��ʼ�����ݿ�
db = SQLAlchemy(app)

# ���벢ע�� Blueprints����ģ�� API��
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

# �������ݿ�������״�����ʱִ�У�
with app.app_context():
    db.create_all()

# ���� Flask ������
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
