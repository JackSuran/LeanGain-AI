#!/usr/bin/env python3
"""
创建MySQL数据库（如果不存在）
请确保MySQL服务正在运行，且.env中的密码正确。
"""
import pymysql
from config import Config

def create_database():
    try:
        conn = pymysql.connect(
            host=Config.DATABASE_HOST,
            user=Config.DATABASE_USER,
            password=Config.DATABASE_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DATABASE_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"数据库 '{Config.DATABASE_NAME}' 创建成功或已存在。")
        cursor.close()
        conn.close()
        return True
    except pymysql.err.OperationalError as e:
        print(f"数据库连接失败: {e}")
        print("请检查MySQL服务是否运行，以及.env中的用户名、密码是否正确。")
        return False

if __name__ == '__main__':
    create_database()