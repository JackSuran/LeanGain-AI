# 故障排除与修复日志

本文档记录了 LeanGain AI 项目中的已知问题、常见问题及其解决方案，以及具体的修复案例。

## 常见问题（FAQ）

### 1. 模板错误 "No filter named 'fromjson'"
此错误已在最新版本中修复。确保你使用的是最新的 `templates/plan/view.html` 和 `app.py`。如果仍出现，请检查 `view_plan` 函数是否正确解析 JSON 并传递 `workout_data`。

### 2. 个人资料已保存但生成计划页面仍提示未填写
确保 `generate_plan` 路由的 GET 请求传递了 `profile` 变量。已修复。

### 3. 导航栏链接 "我的计划" 404
确保 `app.py` 中包含 `/plan` 路由（已实现）。

### 4. 控制台输出乱码
Windows 控制台可能使用 GBK 编码，导致中文字符显示异常。这不会影响功能，可忽略。

### 5. 缓存文件未生成
首次请求运动描述时会调用API并生成缓存。确保 `cache/` 目录可写。

---

## 修复案例

### 案例一：仪表盘“今日训练”模块显示异常

#### 问题描述
用户报告仪表盘中“今日训练”模块数据显示异常，无法准确呈现今日的训练内容、统计数据和进度更新。

#### 诊断步骤
1. **分析项目结构**：查看项目文件布局，确定主要代码文件。
2. **检查仪表盘路由和模板**：审查 `app.py` 中的 `/dashboard` 路由和 `templates/dashboard/index.html` 模板。
3. **检查数据源和模型**：审查 `database/models.py` 中的 `DailyWorkout` 和 `WeeklyPlan` 模型。
4. **检查时间戳处理和缓存**：验证日期字段类型和比较逻辑。
5. **添加日志以验证假设**：在仪表板路由中添加调试日志，输出 `daily_workouts` 和 `now_date` 的实际值。
6. **提出修复方案并实施**：根据诊断结果制定并实施修复。
7. **测试修复**：通过测试脚本验证修复效果。

#### 诊断发现
- 调试日志显示 `daily_workouts` 中存在今日（2025-12-03）的锻炼记录，且 `now_date` 也为同一日期。
- 模板中使用 `{% for dw in daily_workouts if dw.date == now_date %}` 进行过滤，但过滤结果为空，导致显示“今日无安排”。
- 进一步检查发现 `dw.date` 和 `now_date` 虽然都是 `datetime.date` 类型，但 Jinja2 的相等性检查可能因对象比较细节而失败。

#### 根本原因
模板中的日期比较失败，导致无法匹配到今日的锻炼记录。可能的原因包括：
- Jinja2 中日期对象比较的细微差异。
- 数据库返回的 `date` 字段可能是字符串（但实际调试显示已是 `datetime.date`）。
- 时区或时间部分的影响（但字段为纯日期）。

#### 修复方案
##### 1. 确保数据模型中的日期类型一致
修改 `database/models.py` 中的 `DailyWorkout.get_by_week_plan` 方法，将 `date` 字段从字符串转换为 `datetime.date` 对象（如果它是字符串）。

**修改前：**
```python
@staticmethod
def get_by_week_plan(weekly_plan_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        sql = "SELECT * FROM daily_workouts WHERE weekly_plan_id = %s ORDER BY day_number"
        cursor.execute(sql, (weekly_plan_id,))
        workouts = cursor.fetchall()
    conn.close()
    return workouts
```

**修改后：**
```python
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
```

##### 2. 在路由中直接计算今日锻炼
在 `app.py` 的 `dashboard` 路由中，直接计算 `today_workout` 并传递给模板，避免依赖模板过滤。

**修改前：**
```python
return render_template('dashboard/index.html',
                       weight_logs=weight_logs,
                       plan=plan,
                       daily_workouts=daily_workouts,
                       now_date=date.today())
```

**修改后：**
```python
# 计算今日锻炼
today_workout = None
today = date.today()
for dw in daily_workouts:
    if dw['date'] == today:
        today_workout = dw
        break
return render_template('dashboard/index.html',
                       weight_logs=weight_logs,
                       plan=plan,
                       daily_workouts=daily_workouts,
                       now_date=today,
                       today_workout=today_workout)
```

##### 3. 修改模板使用 today_workout
更新 `templates/dashboard/index.html` 中“今日训练”部分，使用 `today_workout` 变量。

**修改前：**
```jinja2
{% set today = none %}
{% for dw in daily_workouts if dw.date == now_date %}
    {% set today = dw %}
{% endfor %}
{% if today %}
    ... 显示今日训练 ...
{% else %}
    <p class="text-muted">今日无安排或计划未生成。</p>
{% endif %}
```

**修改后：**
```jinja2
{% if today_workout %}
    <h6>第 {{ today_workout.day_number }} 天 · {{ today_workout.focus if today_workout.focus else '全身' }}</h6>
    <p class="small">{{ today_workout.workout_json | tojson | safe }}</p>
    {% if not today_workout.completed %}
    <form method="POST" action="{{ url_for('complete_daily', daily_id=today_workout.id) }}">
        <button type="submit" class="btn btn-success btn-sm">标记完成</button>
    </form>
    {% else %}
    <span class="badge bg-success">已完成</span>
    {% endif %}
{% else %}
    <p class="text-muted">今日无安排或计划未生成。</p>
{% endif %}
```

#### 测试验证
编写测试脚本 `check_today.py`，模拟登录用户访问仪表板，检查响应中是否包含“今日无安排”文本。修复后测试结果：
- `Response contains 今日无安排? False`
- `Response contains 第 天? True`
- 卡片体显示今日训练内容（第1天，焦点“全身”等）。

确认“今日训练”模块已能正确显示今日的训练内容、统计数据和进度更新。

#### 影响范围
- 仅影响仪表盘中的“今日训练”模块，不影响其他功能。
- 修复后，今日训练模块将正确显示当天的锻炼计划，包括完成状态和标记完成按钮。

#### 后续建议
- 考虑在模型层统一日期字段类型，避免类似问题。
- 可增加单元测试覆盖日期比较逻辑。
- 监控生产环境中日期相关问题的出现。

---

**修复时间**：2025-12-02  
**修复人员**：Roo (AI助手)  
**版本**：1.0