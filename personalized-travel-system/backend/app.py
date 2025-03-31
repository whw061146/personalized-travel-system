import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# 导入数据库实例
from models import db

# 导入蓝图注册函数
from routes import register_blueprints

def create_app(config_name=None):
    """创建Flask应用实例"""
    app = Flask(__name__)
    
    # 配置应用
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')
    
    # 从config.py加载配置
    app.config.from_object(f'config.{config_name.capitalize()}Config')
    
    # 配置跨域资源共享(CORS)
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # 初始化数据库
    db.init_app(app)
    
    # 初始化JWT认证
    jwt = JWTManager(app)
    
    # 注册所有蓝图
    register_blueprints(app)
    
    # 添加健康检查端点
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'ok',
            'message': '个性化旅游推荐系统API服务正常运行'
        })
    
    return app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 配置应用运行参数
    app.run(
        host=os.environ.get('FLASK_HOST', '0.0.0.0'),
        port=int(os.environ.get('FLASK_PORT', 5000)),
        debug=os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    )