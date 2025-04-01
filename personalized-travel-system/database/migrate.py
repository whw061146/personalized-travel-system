#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库迁移脚本
用于实现数据库迁移功能、版本控制、向前和向后迁移，并记录迁移日志
"""

import os
import sys
import json
import time
import logging
import argparse
import pymysql
import sqlite3
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入配置
from backend.config import DevelopmentConfig, ProductionConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent / 'migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('db_migration')

# 迁移版本表名
MIGRATION_TABLE = 'db_migrations'

# 迁移脚本目录
MIGRATION_DIR = Path(__file__).parent / 'migrations'


def get_db_connection(config):
    """获取数据库连接
    
    Args:
        config: 配置对象，包含数据库连接信息
    
    Returns:
        connection: 数据库连接对象
        is_sqlite: 是否为SQLite数据库
    """
    db_uri = config.SQLALCHEMY_DATABASE_URI
    is_sqlite = 'sqlite' in db_uri
    
    try:
        if is_sqlite:
            # SQLite数据库连接
            db_path = db_uri.replace('sqlite:///', '')
            connection = sqlite3.connect(db_path)
            # 启用外键约束
            connection.execute("PRAGMA foreign_keys = ON")
            # 行工厂设置为字典
            connection.row_factory = sqlite3.Row
        else:
            # MySQL数据库连接
            db_info = db_uri.replace('mysql+pymysql://', '').split('@')
            auth_info = db_info[0].split(':')
            conn_info = db_info[1].split('/')
            
            username = auth_info[0]
            password = auth_info[1] if len(auth_info) > 1 else ''
            host = conn_info[0]
            dbname = conn_info[1] if len(conn_info) > 1 else 'travel_system'
            
            connection = pymysql.connect(
                host=host,
                user=username,
                password=password,
                database=dbname,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
        
        return connection, is_sqlite
    
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        return None, is_sqlite


def ensure_migration_table(connection, is_sqlite):
    """确保迁移版本表存在
    
    Args:
        connection: 数据库连接对象
        is_sqlite: 是否为SQLite数据库
    
    Returns:
        bool: 操作是否成功
    """
    try:
        cursor = connection.cursor()
        
        # 检查迁移表是否存在
        if is_sqlite:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{MIGRATION_TABLE}'")
        else:
            cursor.execute(f"SHOW TABLES LIKE '{MIGRATION_TABLE}'")
        
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            # 创建迁移版本表
            if is_sqlite:
                cursor.execute(f"""
                CREATE TABLE {MIGRATION_TABLE} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version VARCHAR(50) NOT NULL,
                    description TEXT,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_applied BOOLEAN DEFAULT 1
                )
                """)
            else:
                cursor.execute(f"""
                CREATE TABLE {MIGRATION_TABLE} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    version VARCHAR(50) NOT NULL,
                    description TEXT,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_applied BOOLEAN DEFAULT TRUE,
                    INDEX idx_version (version)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
            
            connection.commit()
            logger.info(f"已创建迁移版本表 {MIGRATION_TABLE}")
        
        return True
    
    except Exception as e:
        logger.error(f"确保迁移表存在时出错: {e}")
        return False


def get_current_version(connection):
    """获取当前数据库版本
    
    Args:
        connection: 数据库连接对象
    
    Returns:
        str: 当前版本号，如果没有则返回None
    """
    try:
        cursor = connection.cursor()
        cursor.execute(f"SELECT version FROM {MIGRATION_TABLE} WHERE is_applied = 1 ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        
        if result:
            return result['version']
        return None
    
    except Exception as e:
        logger.error(f"获取当前版本时出错: {e}")
        return None


def get_available_migrations():
    """获取所有可用的迁移脚本
    
    Returns:
        list: 迁移脚本列表，按版本号排序
    """
    # 确保迁移目录存在
    MIGRATION_DIR.mkdir(exist_ok=True)
    
    migrations = []
    for file_path in MIGRATION_DIR.glob('*.sql'):
        # 文件名格式: V{version}__{description}.sql
        # 例如: V1.0.0__initial_schema.sql
        file_name = file_path.name
        if file_name.startswith('V') and '__' in file_name:
            version = file_name.split('__')[0][1:]
            description = file_name.split('__')[1].replace('.sql', '')
            migrations.append({
                'version': version,
                'description': description.replace('_', ' '),
                'file_path': file_path
            })
    
    # 按版本号排序
    return sorted(migrations, key=lambda x: [int(n) for n in x['version'].split('.')])


def apply_migration(connection, is_sqlite, migration):
    """应用迁移脚本
    
    Args:
        connection: 数据库连接对象
        is_sqlite: 是否为SQLite数据库
        migration: 迁移脚本信息
    
    Returns:
        bool: 操作是否成功
    """
    try:
        # 读取迁移脚本内容
        with open(migration['file_path'], 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        cursor = connection.cursor()
        
        # 执行迁移脚本
        if is_sqlite:
            connection.executescript(sql_content)
        else:
            # 分割SQL语句并执行
            for statement in sql_content.split(';'):
                if statement.strip():
                    cursor.execute(statement)
        
        # 记录迁移版本
        cursor.execute(
            f"INSERT INTO {MIGRATION_TABLE} (version, description, applied_at, is_applied) VALUES (?, ?, ?, ?)"
            if is_sqlite else
            f"INSERT INTO {MIGRATION_TABLE} (version, description, applied_at, is_applied) VALUES (%s, %s, %s, %s)",
            (migration['version'], migration['description'], datetime.now(), True)
        )
        
        connection.commit()
        logger.info(f"已应用迁移: {migration['version']} - {migration['description']}")
        return True
    
    except Exception as e:
        connection.rollback()
        logger.error(f"应用迁移 {migration['version']} 时出错: {e}")
        return False


def revert_migration(connection, is_sqlite, migration):
    """回滚迁移脚本
    
    Args:
        connection: 数据库连接对象
        is_sqlite: 是否为SQLite数据库
        migration: 迁移脚本信息
    
    Returns:
        bool: 操作是否成功
    """
    # 查找对应的回滚脚本 R{version}__{description}.sql
    revert_file = migration['file_path'].parent / f"R{migration['version']}__{migration['description'].replace(' ', '_')}.sql"
    
    if not revert_file.exists():
        logger.error(f"回滚脚本不存在: {revert_file}")
        return False
    
    try:
        # 读取回滚脚本内容
        with open(revert_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        cursor = connection.cursor()
        
        # 执行回滚脚本
        if is_sqlite:
            connection.executescript(sql_content)
        else:
            # 分割SQL语句并执行
            for statement in sql_content.split(';'):
                if statement.strip():
                    cursor.execute(statement)
        
        # 更新迁移记录
        cursor.execute(
            f"UPDATE {MIGRATION_TABLE} SET is_applied = ? WHERE version = ?"
            if is_sqlite else
            f"UPDATE {MIGRATION_TABLE} SET is_applied = %s WHERE version = %s",
            (False, migration['version'])
        )
        
        connection.commit()
        logger.info(f"已回滚迁移: {migration['version']} - {migration['description']}")
        return True
    
    except Exception as e:
        connection.rollback()
        logger.error(f"回滚迁移 {migration['version']} 时出错: {e}")
        return False


def create_migration_script(version, description):
    """创建新的迁移脚本
    
    Args:
        version: 版本号
        description: 描述
    
    Returns:
        tuple: (迁移脚本路径, 回滚脚本路径)
    """
    # 确保迁移目录存在
    MIGRATION_DIR.mkdir(exist_ok=True)
    
    # 格式化描述为文件名
    file_description = description.replace(' ', '_').lower()
    
    # 创建迁移脚本文件
    migration_file = MIGRATION_DIR / f"V{version}__{file_description}.sql"
    revert_file = MIGRATION_DIR / f"R{version}__{file_description}.sql"
    
    # 写入模板内容
    if not migration_file.exists():
        with open(migration_file, 'w', encoding='utf-8') as f:
            f.write(f"-- 迁移脚本: {description}\n")
            f.write(f"-- 版本: {version}\n")
            f.write(f"-- 创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("-- 在此处添加SQL语句\n")
    
    if not revert_file.exists():
        with open(revert_file, 'w', encoding='utf-8') as f:
            f.write(f"-- 回滚脚本: {description}\n")
            f.write(f"-- 版本: {version}\n")
            f.write(f"-- 创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("-- 在此处添加回滚SQL语句\n")
    
    logger.info(f"已创建迁移脚本: {migration_file}")
    logger.info(f"已创建回滚脚本: {revert_file}")
    
    return migration_file, revert_file


def migrate(config, target_version=None):
    """执行数据库迁移
    
    Args:
        config: 配置对象，包含数据库连接信息
        target_version: 目标版本，如果为None则迁移到最新版本
    
    Returns:
        bool: 操作是否成功
    """
    connection, is_sqlite = get_db_connection(config)
    if not connection:
        return False
    
    try:
        # 确保迁移表存在
        if not ensure_migration_table(connection, is_sqlite):
            return False
        
        # 获取当前版本
        current_version = get_current_version(connection)
        logger.info(f"当前数据库版本: {current_version or '未初始化'}")
        
        # 获取可用迁移脚本
        available_migrations = get_available_migrations()
        if not available_migrations:
            logger.info("没有可用的迁移脚本")
            return True
        
        # 确定目标版本
        if target_version is None:
            target_version = available_migrations[-1]['version']
        
        logger.info(f"目标数据库版本: {target_version}")
        
        # 如果当前版本为None，从第一个迁移开始
        if current_version is None:
            for migration in available_migrations:
                if not apply_migration(connection, is_sqlite, migration):
                    return False
                
                if migration['version'] == target_version:
                    break
        else:
            # 确定当前版本在迁移列表中的位置
            current_index = -1
            target_index = -1
            
            for i, migration in enumerate(available_migrations):
                if migration['version'] == current_version:
                    current_index = i
                if migration['version'] == target_version:
                    target_index = i
            
            if current_index == -1:
                logger.error(f"当前版本 {current_version} 不在迁移列表中")
                return False
            
            if target_index == -1:
                logger.error(f"目标版本 {target_version} 不在迁移列表中")
                return False
            
            # 向前迁移
            if target_index > current_index:
                for i in range(current_index + 1, target_index + 1):
                    if not apply_migration(connection, is_sqlite, available_migrations[i]):
                        return False
            # 向后迁移（回滚）
            elif target_index < current_index:
                for i in range(current_index, target_index, -1):
                    if not revert_migration(connection, is_sqlite, available_migrations[i]):
                        return False
        
        logger.info(f"数据库已成功迁移到版本: {target_version}")
        return True
    
    except Exception as e:
        logger.error(f"执行迁移时出错: {e}")
        return False
    
    finally:
        if connection:
            connection.close()


def main():
    """主函数，处理命令行参数并执行数据库迁移"""
    parser = argparse.ArgumentParser(description='数据库迁移工具')
    parser.add_argument('--env', choices=['dev', 'prod'], default='dev',
                        help='环境配置: dev (开发) 或 prod (生产)')
    
    subparsers = parser.add_subparsers(dest='command', help='迁移命令')
    
    # migrate命令
    migrate_parser = subparsers.add_parser('migrate', help='执行数据库迁移')
    migrate_parser.add_argument('--to', dest='target_version',
                               help='迁移到指定版本，默认为最新版本')
    
    # create命令
    create_parser = subparsers.add_parser('create', help='创建新的迁移脚本')
    create_parser.add_argument('version', help='版本号，例如: 1.0.0')
    create_parser.add_argument('description', help='迁移描述')
    
    # info命令
    info_parser = subparsers.add_parser('info', help='显示迁移信息')
    
    args = parser.parse_args()
    
    # 根据环境选择配置
    config = DevelopmentConfig if args.env == 'dev' else ProductionConfig
    
    print(f"使用 {args.env} 环境配置")
    print(f"数据库URI: {config.SQLALCHEMY_DATABASE_URI}")
    
    if args.command == 'migrate':
        # 执行迁移
        if migrate(config, args.target_version):
            print("数据库迁移成功！")
        else:
            print("数据库迁移失败！")
    
    elif args.command == 'create':
        # 创建迁移脚本
        migration_file, revert_file = create_migration_script(args.version, args.description)
        print(f"已创建迁移脚本: {migration_file}")
        print(f"已创建回滚脚本: {revert_file}")
        print("请编辑这些文件，添加必要的SQL语句")
    
    elif args.command == 'info':
        # 显示迁移信息
        connection, is_sqlite = get_db_connection(config)
        if not connection:
            print("无法连接到数据库")
            return
        
        try:
            # 确保迁移表存在
            ensure_migration_table(connection, is_sqlite)
            
            # 获取当前版本
            current_version = get_current_version(connection)
            print(f"当前数据库版本: {current_version or '未初始化'}")
            
            # 获取可用迁移脚本
            available_migrations = get_available_migrations()
            print(f"可用迁移脚本数量: {len(available_migrations)}")
            
            if available_migrations:
                print("\n可用迁移脚本:")
                for migration in available_migrations:
                    status = "[当前]" if migration['version'] == current_version else ""
                    print(f"  {migration['version']} - {migration['description']} {status}")
        
        finally:
            if connection:
                connection.close()
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()