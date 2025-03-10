from backend.app import app

if __name__ == "__main__":
    app.run()

# 生产环境 WSGI 入口，供 Gunicorn 或其他 WSGI 服务器使用
# 部署时，使用如下命令启动：
# gunicorn --bind 0.0.0.0:5000 wsgi:app
