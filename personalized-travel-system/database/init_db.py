#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库初始化脚本
用于创建数据库、执行schema.sql脚本、添加初始管理员账户
并提供数据库连接测试功能
"""

import os
import sys
import pymysql
import argparse
from pathlib import Path
from flask_bcrypt import generate_password_hash

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入配置
from backend.config import DevelopmentConfig, ProductionConfig


def create_database(config, drop_existing=False):
    """创建数据库
    
    Args:
        config: 配置对象，包含数据库连接信息
        drop_existing: 是否删除已存在的数据库
    
    Returns:
        bool: 操作是否成功
    """
    # 从数据库URI中提取连接信息
    # 格式: mysql+pymysql://username:password@host/dbname
    db_uri = config.SQLALCHEMY_DATABASE_URI
    if 'sqlite' in db_uri:
        print("SQLite数据库不需要预先创建，跳过此步骤")
        return True
    
    try:
        # 解析数据库URI
        db_info = db_uri.replace('mysql+pymysql://', '').split('@')
        auth_info = db_info[0].split(':')
        conn_info = db_info[1].split('/')
        
        username = auth_info[0]
        password = auth_info[1] if len(auth_info) > 1 else ''
        host = conn_info[0]
        dbname = conn_info[1] if len(conn_info) > 1 else 'travel_system'
        
        # 连接到MySQL服务器（不指定数据库）
        connection = pymysql.connect(
            host=host,
            user=username,
            password=password,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            if drop_existing:
                cursor.execute(f"DROP DATABASE IF EXISTS {dbname}")
                print(f"已删除数据库 {dbname}")
            
            # 创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {dbname} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"已创建数据库 {dbname}")
            
            # 使用该数据库
            cursor.execute(f"USE {dbname}")
            
        connection.close()
        return True
    
    except Exception as e:
        print(f"创建数据库时出错: {e}")
        return False


def execute_schema_script(config):
    """执行schema.sql脚本
    
    Args:
        config: 配置对象，包含数据库连接信息
    
    Returns:
        bool: 操作是否成功
    """
    db_uri = config.SQLALCHEMY_DATABASE_URI
    schema_path = project_root / 'backend' / 'schema.sql'
    
    if not schema_path.exists():
        print(f"错误: schema.sql文件不存在于 {schema_path}")
        return False
    
    try:
        # 读取schema.sql文件内容
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        if 'sqlite' in db_uri:
            # SQLite数据库处理
            import sqlite3
            db_path = db_uri.replace('sqlite:///', '')
            conn = sqlite3.connect(db_path)
            conn.executescript(schema_sql)
            conn.close()
            print(f"已成功执行schema.sql脚本到SQLite数据库: {db_path}")
        else:
            # MySQL数据库处理
            db_info = db_uri.replace('mysql+pymysql://', '').split('@')
            auth_info = db_info[0].split(':')
            conn_info = db_info[1].split('/')
            
            username = auth_info[0]
            password = auth_info[1] if len(auth_info) > 1 else ''
            host = conn_info[0]
            dbname = conn_info[1] if len(conn_info) > 1 else 'travel_system'
            
            # 连接到MySQL数据库
            connection = pymysql.connect(
                host=host,
                user=username,
                password=password,
                database=dbname,
                charset='utf8mb4'
            )
            
            # 执行SQL脚本
            with connection.cursor() as cursor:
                # 分割SQL语句并执行
                for statement in schema_sql.split(';'):
                    if statement.strip():
                        cursor.execute(statement)
                connection.commit()
            
            connection.close()
            print(f"已成功执行schema.sql脚本到MySQL数据库: {dbname}")
        
        return True
    
    except Exception as e:
        print(f"执行schema.sql脚本时出错: {e}")
        return False


def test_database_connection(config):
    """测试数据库连接
    
    Args:
        config: 配置对象，包含数据库连接信息
    
    Returns:
        bool: 连接是否成功
    """
    db_uri = config.SQLALCHEMY_DATABASE_URI
    
    try:
        if 'sqlite' in db_uri:
            # SQLite数据库连接测试
            import sqlite3
            db_path = db_uri.replace('sqlite:///', '')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            conn.close()
            
            print("数据库连接测试成功 (SQLite)")
            print(f"数据库中的表: {[table[0] for table in tables]}")
        else:
            # MySQL数据库连接测试
            db_info = db_uri.replace('mysql+pymysql://', '').split('@')
            auth_info = db_info[0].split(':')
            conn_info = db_info[1].split('/')
            
            username = auth_info[0]
            password = auth_info[1] if len(auth_info) > 1 else ''
            host = conn_info[0]
            dbname = conn_info[1] if len(conn_info) > 1 else 'travel_system'
            
            # 连接到MySQL数据库
            connection = pymysql.connect(
                host=host,
                user=username,
                password=password,
                database=dbname,
                charset='utf8mb4'
            )
            
            with connection.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
            
            connection.close()
            
            print("数据库连接测试成功 (MySQL)")
            print(f"数据库中的表: {[table[0] for table in tables]}")
        
        return True
    
    except Exception as e:
        print(f"数据库连接测试失败: {e}")
        return False


def main():
    """主函数，处理命令行参数并执行数据库初始化"""
    parser = argparse.ArgumentParser(description='初始化旅游推荐系统数据库')
    parser.add_argument('--env', choices=['dev', 'prod'], default='dev',
                        help='环境配置: dev (开发) 或 prod (生产)')
    parser.add_argument('--drop', action='store_true',
                        help='删除已存在的数据库并重新创建')
    parser.add_argument('--test-only', action='store_true',
                        help='仅测试数据库连接，不执行初始化')
    
    args = parser.parse_args()
    
    # 根据环境选择配置
    config = DevelopmentConfig if args.env == 'dev' else ProductionConfig
    
    print(f"使用 {args.env} 环境配置")
    print(f"数据库URI: {config.SQLALCHEMY_DATABASE_URI}")
    
    if args.test_only:
        # 仅测试数据库连接
        test_database_connection(config)
        return
    
    # 创建数据库
    if create_database(config, args.drop):
        # 执行schema.sql脚本
        if execute_schema_script(config):
            # 测试数据库连接
            test_database_connection(config)
            print("数据库初始化完成！")
        else:
            print("数据库初始化失败: 无法执行schema.sql脚本")
    else:
        print("数据库初始化失败: 无法创建数据库")


if __name__ == '__main__':
    main()