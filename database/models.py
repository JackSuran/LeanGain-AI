from database.db_connection import get_db_connection
from datetime import datetime
import json

class User:
    @staticmethod
    def create(username, password_hash, email=None):
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s)"
            cursor.execute(sql, (username, password_hash, email))
            conn.commit()
            user_id = cursor.lastrowid
        conn.close()
        return user_id

    @staticmethod
    def get_by_username(username):
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "SELECT * FROM users WHERE username = %s"
            cursor.execute(sql, (username,))
            user = cursor.fetchone()
        conn.close()
        return user

    @staticmethod
    def get_by_id(user_id):
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "SELECT * FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            user = cursor.fetchone()
        conn.close()
        return user

class UserProfile:
    @staticmethod
    def create_or_update(user_id, **data):
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 检查是否存在
            sql = "SELECT id FROM user_profiles WHERE user_id = %s"
            cursor.execute(sql, (user_id,))
            existing = cursor.fetchone()
            if existing:
                # 更新
                fields = []
                values = []
                for key, value in data.items():
                    if key == 'available_equipment' or key == 'preferences':
                        value = json.dumps(value, ensure_ascii=False)
                    fields.append(f"{key} = %s")
                    values.append(value)
                values.append(user_id)
                sql = f"UPDATE user_profiles SET {', '.join(fields)} WHERE user_id = %s"
                cursor.execute(sql, values)
            else:
                # 插入
                keys = ['user_id']
                placeholders = ['%s']
                vals = [user_id]
                for key, value in data.items():
                    if key == 'available_equipment' or key == 'preferences':
                        value = json.dumps(value, ensure_ascii=False)
                    keys.append(key)
                    placeholders.append('%s')
                    vals.append(value)
                sql = f"INSERT INTO user_profiles ({', '.join(keys)}) VALUES ({', '.join(placeholders)})"
                cursor.execute(sql, vals)
            conn.commit()
        conn.close()

    @staticmethod
    def get_by_user_id(user_id):
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "SELECT * FROM user_profiles WHERE user_id = %s"
            cursor.execute(sql, (user_id,))
            profile = cursor.fetchone()
        conn.close()
        if profile:
            # 解析JSON字段
            for field in ['available_equipment', 'preferences']:
                if profile.get(field):
                    try:
                        profile[field] = json.loads(profile[field])
                    except:
                        pass
        return profile

class WeeklyPlan:
    @staticmethod
    def create(user_id, plan_json, start_date, end_date, is_active=True):
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """INSERT INTO weekly_plans (user_id, plan_json, start_date, end_date, is_active)
                     VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(sql, (user_id, plan_json, start_date, end_date, is_active))
            conn.commit()
            plan_id = cursor.lastrowid
        conn.close()
        return plan_id

    @staticmethod
    def get_active_plan(user_id):
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "SELECT * FROM weekly_plans WHERE user_id = %s AND is_active = TRUE ORDER BY generated_at DESC LIMIT 1"
            cursor.execute(sql, (user_id,))
            plan = cursor.fetchone()
        conn.close()
        return plan

class DailyWorkout:
    @staticmethod
    def create(weekly_plan_id, day_number, date, workout_json):
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """INSERT INTO daily_workouts (weekly_plan_id, day_number, date, workout_json)
                     VALUES (%s, %s, %s, %s)"""
            cursor.execute(sql, (weekly_plan_id, day_number, date, workout_json))
            conn.commit()
            workout_id = cursor.lastrowid
        conn.close()
        return workout_id

    @staticmethod
    def get_by_week_plan(weekly_plan_id):
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "SELECT * FROM daily_workouts WHERE weekly_plan_id = %s ORDER BY day_number"
            cursor.execute(sql, (weekly_plan_id,))
            workouts = cursor.fetchall()
        conn.close()
        # 将date字段从字符串转换为datetime.date
        for w in workouts:
            if w.get('date') and isinstance(w['date'], str):
                w['date'] = datetime.strptime(w['date'], '%Y-%m-%d').date()
        return workouts

class WeightLog:
    @staticmethod
    def add(user_id, weight_kg, notes=''):
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "INSERT INTO weight_logs (user_id, weight_kg, notes) VALUES (%s, %s, %s)"
            cursor.execute(sql, (user_id, weight_kg, notes))
            conn.commit()
        conn.close()

    @staticmethod
    def get_by_user(user_id, limit=30):
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "SELECT * FROM weight_logs WHERE user_id = %s ORDER BY measured_at DESC LIMIT %s"
            cursor.execute(sql, (user_id, limit))
            logs = cursor.fetchall()
        conn.close()
        return logs