from flask_sqlalchemy import SQLAlchemy

# ✅ 这里 **不传入 `app`**，避免重复初始化
db = SQLAlchemy()
