from flask_sqlalchemy import SQLAlchemy

# ✅ 这里 **不传入 `app`**，避免重复初始化
db = SQLAlchemy()

# 导入所有模型，使它们可以直接从models包中导入
from .user import User
from .place import Place
from .food import Food
from .diary import Diary
from .path import Path

# 在app.py中使用init_app方法初始化数据库连接
# 数据库配置从config.py中获取
