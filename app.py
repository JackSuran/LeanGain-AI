from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from config import Config
from database.models import User, UserProfile, WeeklyPlan, DailyWorkout, WeightLog
from database.db_connection import init_database, get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
import json
import os

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

# 初始化数据库
init_database()

# 辅助函数
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录。', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# 首页
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# 关于页面
@app.route('/about')
def about():
    return render_template('about.html')

# 注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        email = request.form.get('email', '').strip()
        if not username or not password:
            flash('用户名和密码不能为空。', 'danger')
            return render_template('auth/register.html')
        existing = User.get_by_username(username)
        if existing:
            flash('用户名已存在。', 'danger')
            return render_template('auth/register.html')
        password_hash = generate_password_hash(password)
        user_id = User.create(username, password_hash, email)
        session['user_id'] = user_id
        session['username'] = username
        flash('注册成功！请完善个人资料。', 'success')
        return redirect(url_for('profile'))
    return render_template('auth/register.html')

# 登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = User.get_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('登录成功！', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('用户名或密码错误。', 'danger')
    return render_template('auth/login.html')

# 退出
@app.route('/logout')
def logout():
    session.clear()
    flash('您已退出登录。', 'info')
    return redirect(url_for('index'))

# 个人资料
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session['user_id']
    profile = UserProfile.get_by_user_id(user_id)
    if request.method == 'POST':
        data = {
            'age': request.form.get('age', type=int),
            'height_cm': request.form.get('height_cm', type=float),
            'current_weight_kg': request.form.get('current_weight_kg', type=float),
            'target_weight_kg': request.form.get('target_weight_kg', type=float),
            'body_fat_percent': request.form.get('body_fat_percent', type=float),
            'training_experience': request.form.get('training_experience'),
        }
        # 处理器械（多选）
        equipment = request.form.getlist('equipment')
        data['available_equipment'] = equipment
        # 偏好
        days_per_week = request.form.get('days_per_week', type=int)
        session_minutes = request.form.get('session_minutes', type=int)
        # 设置默认值
        if days_per_week is None:
            days_per_week = 3
        if session_minutes is None:
            session_minutes = 60
        preferences = {
            'days_per_week': days_per_week,
            'session_minutes': session_minutes,
            'focus': request.form.getlist('focus'),
            'avoid': request.form.get('avoid', '')
        }
        data['preferences'] = preferences
        # 移除None值
        data = {k: v for k, v in data.items() if v is not None}
        UserProfile.create_or_update(user_id, **data)
        flash('个人资料已保存。', 'success')
        return redirect(url_for('profile'))
    return render_template('profile/edit.html', profile=profile)

# 仪表板
@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    # 获取最新体重
    weight_logs = WeightLog.get_by_user(user_id, limit=10)
    # 获取活跃计划
    plan = WeeklyPlan.get_active_plan(user_id)
    daily_workouts = []
    if plan:
        daily_workouts = DailyWorkout.get_by_week_plan(plan['id'])
    # 调试日志
    import sys
    print(f"[DEBUG] user_id={user_id}, plan={plan}", file=sys.stderr)
    print(f"[DEBUG] daily_workouts count={len(daily_workouts)}", file=sys.stderr)
    for dw in daily_workouts:
        print(f"[DEBUG]   id={dw['id']}, date={dw['date']}, day_number={dw['day_number']}, completed={dw.get('completed')}", file=sys.stderr)
    print(f"[DEBUG] now_date={date.today()}", file=sys.stderr)
    # 计算今日锻炼
    today_workout = None
    today = date.today()
    for dw in daily_workouts:
        if dw['date'] == today:
            today_workout = dw
            break
    # 解析今日锻炼的JSON
    if today_workout and today_workout.get('workout_json'):
        try:
            today_workout['workout_data'] = json.loads(today_workout['workout_json'])
            # 同时将focus字段提取到顶层方便模板使用
            today_workout['focus'] = today_workout['workout_data'].get('focus', '')
        except:
            today_workout['workout_data'] = {'focus': '未知', 'exercises': []}
            today_workout['focus'] = '未知'
    elif today_workout:
        today_workout['workout_data'] = {'focus': '未知', 'exercises': []}
        today_workout['focus'] = '未知'
    return render_template('dashboard/index.html',
                           weight_logs=weight_logs,
                           plan=plan,
                           daily_workouts=daily_workouts,
                           now_date=today,
                           today_workout=today_workout)

# 生成计划页面
@app.route('/plan/generate', methods=['GET', 'POST'])
@login_required
def generate_plan():
    user_id = session['user_id']
    profile = UserProfile.get_by_user_id(user_id)
    if request.method == 'POST':
        if not profile:
            flash('请先填写个人资料。', 'warning')
            return redirect(url_for('profile'))
        # 调用DeepSeek服务生成计划
        from services.deepseek_service import generate_workout_plan
        # 生成计划
        plan_json = generate_workout_plan(profile)
        if not plan_json:
            flash('生成计划失败，请稍后重试。', 'danger')
            return redirect(url_for('generate_plan'))
        # 解析计划并存入数据库
        plan_data = json.loads(plan_json)
        start_date = date.today()
        end_date = start_date + timedelta(days=6)
        plan_id = WeeklyPlan.create(user_id, plan_json, start_date, end_date, True)
        # 创建每日锻炼
        for day in plan_data.get('days', []):
            DailyWorkout.create(plan_id, day['day'], start_date + timedelta(days=day['day']-1), json.dumps(day))
        flash('周计划已生成！', 'success')
        return redirect(url_for('view_plan', plan_id=plan_id))
    # GET请求：传递个人资料给模板
    return render_template('plan/generate.html', profile=profile)

# 我的计划（重定向到活跃计划或生成页面）
@app.route('/plan')
@login_required
def plan():
    user_id = session['user_id']
    plan = WeeklyPlan.get_active_plan(user_id)
    if plan:
        return redirect(url_for('view_plan', plan_id=plan['id']))
    else:
        flash('您还没有任何计划，请先生成一个计划。', 'info')
        return redirect(url_for('generate_plan'))

# 查看计划
@app.route('/plan/<int:plan_id>')
@login_required
def view_plan(plan_id):
    # 验证计划属于当前用户
    plan = WeeklyPlan.get_active_plan(session['user_id'])
    if not plan or plan['id'] != plan_id:
        flash('计划不存在或无权访问。', 'danger')
        return redirect(url_for('dashboard'))
    daily_workouts = DailyWorkout.get_by_week_plan(plan_id)
    # 解析每个daily_workout的workout_json
    for dw in daily_workouts:
        if dw.get('workout_json'):
            try:
                dw['workout_data'] = json.loads(dw['workout_json'])
            except:
                dw['workout_data'] = {'focus': '未知', 'exercises': []}
        else:
            dw['workout_data'] = {'focus': '未知', 'exercises': []}
    return render_template('plan/view.html', plan=plan, daily_workouts=daily_workouts)

# 完成每日锻炼
@app.route('/daily/<int:daily_id>/complete', methods=['POST'])
@login_required
def complete_daily(daily_id):
    # 验证所有权
    # 简化为直接更新
    conn = get_db_connection()
    with conn.cursor() as cursor:
        sql = "UPDATE daily_workouts SET completed = TRUE, completion_time = NOW() WHERE id = %s"
        cursor.execute(sql, (daily_id,))
        conn.commit()
    conn.close()
    flash('锻炼已完成！', 'success')
    return redirect(request.referrer or url_for('dashboard'))

# 记录体重
@app.route('/weight/log', methods=['POST'])
@login_required
def log_weight():
    weight = request.form.get('weight', type=float)
    notes = request.form.get('notes', '')
    if weight and 20 <= weight <= 300:
        WeightLog.add(session['user_id'], weight, notes)
        flash('体重记录已保存。', 'success')
    else:
        flash('请输入有效的体重（20-300公斤）。', 'danger')
    return redirect(url_for('dashboard'))

# 获取运动介绍
@app.route('/exercise/description', methods=['GET', 'POST'])
@login_required
def exercise_description():
    """
    返回运动的详细介绍。
    GET参数或POST JSON: exercise_name
    需要用户已登录，使用其个人资料。
    """
    if request.method == 'GET':
        exercise_name = request.args.get('exercise_name')
    else:
        data = request.get_json()
        if not data:
            exercise_name = request.form.get('exercise_name')
        else:
            exercise_name = data.get('exercise_name')
    if not exercise_name:
        return jsonify({'error': '缺少运动名称参数 exercise_name'}), 400
    user_id = session['user_id']
    profile = UserProfile.get_by_user_id(user_id)
    if not profile:
        return jsonify({'error': '用户资料不存在，请先填写个人资料'}), 400
    # 调用DeepSeek服务生成介绍
    from services.deepseek_service import generate_exercise_description
    try:
        description, cached = generate_exercise_description(exercise_name, profile)
        return jsonify({
            'exercise_name': exercise_name,
            'description': description,
            'cached': cached
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': '生成介绍时发生错误', 'details': str(e)}), 500

# 初始化数据库路由（仅开发用）
@app.route('/initdb')
def initdb():
    init_database()
    return 'Database tables created.'

if __name__ == '__main__':
    app.run(debug=True)