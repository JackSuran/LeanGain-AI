import pymysql
import pymysql.cursors
from config import Config

def get_db_connection():
    """返回一个MySQL数据库连接"""
    return pymysql.connect(
        host=Config.DATABASE_HOST,
        user=Config.DATABASE_USER,
        password=Config.DATABASE_PASSWORD,
        database=Config.DATABASE_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        charset='utf8mb4'
    )

def execute_query(query, args=None, fetchone=False, fetchall=False):
    """执行SQL查询并返回结果"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, args)
            if fetchone:
                result = cursor.fetchone()
            elif fetchall:
                result = cursor.fetchall()
            else:
                result = None
            conn.commit()
            return result
    finally:
        conn.close()

def init_database():
    """初始化所有表（如果不存在）"""
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # user_profiles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                age INT,
                height_cm DECIMAL(5,2),
                current_weight_kg DECIMAL(5,2),
                target_weight_kg DECIMAL(5,2),
                body_fat_percent DECIMAL(4,2),
                available_equipment TEXT,
                training_experience ENUM('beginner','intermediate','advanced'),
                preferences TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        # weekly_plans
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_plans (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                plan_json TEXT,
                generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                start_date DATE,
                end_date DATE,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        # daily_workouts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_workouts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                weekly_plan_id INT NOT NULL,
                day_number INT,
                date DATE,
                workout_json TEXT,
                completed BOOLEAN DEFAULT FALSE,
                completion_time DATETIME,
                user_notes TEXT,
                FOREIGN KEY (weekly_plan_id) REFERENCES weekly_plans(id) ON DELETE CASCADE
            )
        ''')
        # weight_logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weight_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                weight_kg DECIMAL(5,2),
                measured_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        # exercise_logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercise_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                daily_workout_id INT NOT NULL,
                exercise_name VARCHAR(100),
                sets INT,
                reps INT,
                weight_kg DECIMAL(5,2),
                completed BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (daily_workout_id) REFERENCES daily_workouts(id) ON DELETE CASCADE
            )
        ''')
        conn.commit()
    conn.close()
    print("MySQL数据库表初始化完成。")

if __name__ == '__main__':
    init_database()