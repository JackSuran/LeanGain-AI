# 瘦子增重增肌锻炼系统 - 项目规划
> 本文档为项目初始规划，实际实现可能有所调整。最新信息请参阅 [README.md](README.md)。


## 技术栈
- 后端：Flask (Python 3.8+)
- 数据库：MySQL (使用PyMySQL驱动)
- 虚拟环境：venv
- AI集成：OpenAI SDK (兼容DeepSeek API) + httpx 0.27.x
- 前端：HTML5, CSS3, JavaScript (使用Bootstrap 5简化)
- 其他：Jinja2模板，SQLAlchemy可选（但使用PyMySQL直接操作）

## 系统功能
1. 用户管理：注册、登录、个人资料
2. 用户数据收集：
   - 身体数据（年龄、身高、当前体重、目标体重、体脂率等）
   - 可用器械（家庭/健身房，具体器械列表）
   - 历史锻炼记录
   - 用户偏好（训练频率、时长、目标部位等）
3. 智能计划生成：
   - 调用DeepSeek API，基于用户数据生成一周锻炼计划
   - 计划包括每日训练内容（动作、组数、次数、休息时间）
4. 计划分解与跟踪：
   - 将周计划分解到每天
   - 每日打卡，记录完成情况、感受、体重变化
5. 数据统计与可视化：
   - 体重变化曲线
   - 训练进度图表
6. 调整与重新生成：
   - 根据体重变化和用户反馈调整计划

## 数据库设计
### 表结构
1. `users`
   - id (INT PRIMARY KEY AUTO_INCREMENT)
   - username (VARCHAR(50) UNIQUE)
   - password_hash (VARCHAR(255))
   - email (VARCHAR(100))
   - created_at (DATETIME)

2. `user_profiles`
   - id (INT PRIMARY KEY AUTO_INCREMENT)
   - user_id (INT FOREIGN KEY)
   - age (INT)
   - height_cm (DECIMAL(5,2))
   - current_weight_kg (DECIMAL(5,2))
   - target_weight_kg (DECIMAL(5,2))
   - body_fat_percent (DECIMAL(4,2))
   - available_equipment (TEXT) JSON格式
   - training_experience (ENUM('beginner','intermediate','advanced'))
   - preferences (TEXT) JSON格式
   - updated_at (DATETIME)

3. `weekly_plans`
   - id (INT PRIMARY KEY AUTO_INCREMENT)
   - user_id (INT FOREIGN KEY)
   - plan_json (TEXT) 周计划完整JSON
   - generated_at (DATETIME)
   - start_date (DATE)
   - end_date (DATE)
   - is_active (BOOLEAN)

4. `daily_workouts`
   - id (INT PRIMARY KEY AUTO_INCREMENT)
   - weekly_plan_id (INT FOREIGN KEY)
   - day_number (INT) 1-7
   - date (DATE)
   - workout_json (TEXT) 当日训练详情
   - completed (BOOLEAN DEFAULT FALSE)
   - completion_time (DATETIME NULL)
   - user_notes (TEXT)

5. `weight_logs`
   - id (INT PRIMARY KEY AUTO_INCREMENT)
   - user_id (INT FOREIGN KEY)
   - weight_kg (DECIMAL(5,2))
   - measured_at (DATETIME)
   - notes (TEXT)

6. `exercise_logs`
   - id (INT PRIMARY KEY AUTO_INCREMENT)
   - daily_workout_id (INT FOREIGN KEY)
   - exercise_name (VARCHAR(100))
   - sets (INT)
   - reps (INT)
   - weight_kg (DECIMAL(5,2))
   - completed (BOOLEAN)

## 目录结构
```
project/
├── app.py                  # Flask主应用
├── config.py               # 配置
├── requirements.txt        # 依赖
├── .env                    # 环境变量
├── .gitignore
├── venv/                   # 虚拟环境
├── database/
│   ├── db_connection.py    # 数据库连接
│   ├── models.py           # 数据模型
│   └── init_db.py          # 初始化数据库
├── services/
│   ├── deepseek_service.py # DeepSeek API调用
│   └── plan_generator.py   # 计划生成逻辑
├── routes/
│   ├── auth.py             # 认证路由
│   ├── profile.py          # 用户资料
│   ├── plan.py             # 计划管理
│   └── dashboard.py        # 仪表板
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── auth/
│   ├── profile/
│   └── dashboard/
└── utils/
    ├── helpers.py
    └── validators.py
```

## API端点设计
- GET / : 首页
- GET /login, POST /login : 登录
- GET /register, POST /register : 注册
- GET /profile : 查看/编辑个人资料
- POST /generate_plan : 生成周计划
- GET /plan/:id : 查看周计划
- GET /daily/:day : 查看每日训练
- POST /complete_day : 标记完成
- POST /log_weight : 记录体重
- GET /dashboard : 数据仪表板

## 下一步
1. 创建虚拟环境和依赖文件
2. 设置项目目录结构
3. 实现数据库模型和初始化