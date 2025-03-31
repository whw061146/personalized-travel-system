# 配置生产环境WSGI入口
# 导入app实例供Gunicorn使用

import os

# 设置环境变量，确保使用生产环境配置
os.environ['FLASK_CONFIG'] = 'production'

# 从app.py导入Flask应用实例
from app import app

# 此文件作为Gunicorn的入口点
# 使用方式: gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
# 其中 -w 4 表示使用4个worker进程
# -b 0.0.0.0:5000 表示绑定到所有网络接口的5000端口

if __name__ == "__main__":
    # 直接运行此文件时，以生产模式启动应用
    # 注意：生产环境应该使用Gunicorn而不是直接运行此文件
    app.run(
        host=os.environ.get('FLASK_HOST', '0.0.0.0'),
        port=int(os.environ.get('FLASK_PORT', 5000)),
        debug=False  # 生产环境禁用调试模式
    )