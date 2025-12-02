# 瘦子增重增肌锻炼系统

一个基于Flask + PyMySQL + DeepSeek AI的个人健身计划系统，专为瘦子（外胚型）设计，帮助用户科学增重增肌。

## 功能特性

- **用户管理**：注册、登录、个人资料管理
- **智能计划生成**：利用DeepSeek AI根据用户身体数据、可用器械、训练经验生成个性化周锻炼计划
- **计划分解与跟踪**：将周计划分解到每一天，支持打卡完成、记录体重变化
- **数据可视化**：体重趋势图表、训练完成度进度条
- **灵活调整**：可根据反馈重新生成计划
- **缓存机制**：使用本地JSON缓存存储运动描述，减少API调用

## 技术栈

- 后端：Flask (Python)
- 数据库：MySQL (PyMySQL驱动)
- AI集成：OpenAI SDK + httpx (调用DeepSeek API)
- 前端：Bootstrap 5, Chart.js, Jinja2模板
- 开发工具：venv, python-dotenv, Git

## 项目结构

```
project/
├── app.py                 # Flask主应用
├── config.py              # 配置类
├── requirements.txt       # Python依赖
├── .env.example          # 环境变量示例
├── .gitignore            # Git忽略规则
├── create_database.py    # 数据库创建脚本
├── FIX_LOG.md            # 修复日志
├── PROJECT_PLAN.md       # 项目计划文档
├── README.md             # 项目说明
├── database/             # 数据库相关
│   ├── db_connection.py  # 数据库连接
│   └── models.py         # 数据模型
├── services/             # 业务服务
│   ├── __init__.py
│   ├── cache_service.py  # 缓存服务
│   └── deepseek_service.py # DeepSeek API调用
├── static/               # 静态资源
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── images/
├── templates/            # Jinja2模板
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── dashboard/
│   │   └── index.html
│   ├── plan/
│   │   ├── generate.html
│   │   └── view.html
│   ├── profile/
│   │   └── edit.html
│   ├── about.html
│   ├── base.html
│   └── index.html
└── cache/                # 缓存目录（Git忽略）
    └── exercise_descriptions/
```

## 快速开始

### 1. 环境准备

- Python 3.8+
- MySQL 5.7+ (确保服务运行)
- DeepSeek API密钥（从[DeepSeek平台](https://platform.deepseek.com/)获取）

### 2. 克隆项目

```bash
git clone <repository-url>
cd body-build
```

### 3. 创建虚拟环境并安装依赖

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### 4. 配置环境变量

复制`.env.example`（或直接编辑`.env`）并设置你的数据库和API密钥：

```bash
cp .env.example .env
```

编辑`.env`文件：

```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this
DATABASE_HOST=localhost
DATABASE_USER=root
DATABASE_PASSWORD=yourpassword
DATABASE_NAME=bodybuilding
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

### 5. 初始化数据库

确保MySQL服务运行，并创建数据库：

```sql
CREATE DATABASE bodybuilding;
```

然后运行数据库创建脚本（创建数据库和表）：

```bash
python create_database.py
python -c "from database.db_connection import init_database; init_database()"
```

或者，你也可以直接访问 `/initdb` 路由（仅开发）来自动初始化。

### 6. 运行应用

```bash
python app.py
```

访问 http://127.0.0.1:5000

### 7. 使用流程

1. 注册新账号
2. 填写个人资料（身高、体重、目标、可用器械等）
3. 点击“生成计划”获取AI生成的周计划
4. 查看仪表板，每日打卡，记录体重
5. 根据进展调整计划

## 配置说明

### MySQL连接问题

如果遇到数据库连接错误，请检查：
- MySQL服务是否运行
- `.env`中的用户名、密码、主机名是否正确
- 数据库`bodybuilding`是否存在

### DeepSeek API

你需要注册DeepSeek平台并获取API密钥。将密钥填入`.env`的`DEEPSEEK_API_KEY`。

如果无法访问DeepSeek，系统会使用默认计划（模拟数据）。

## 故障排除

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

## 开发

### 运行测试
目前暂无自动化测试套件，但可以手动测试各功能。

### 代码风格
遵循PEP 8，使用Black进行格式化（可选）。

### 添加新功能
1. 创建功能分支：`git checkout -b feature/your-feature`
2. 进行更改并提交
3. 推送到远程并创建Pull Request

## 部署到生产环境

建议使用Gunicorn + Nginx部署。

1. 安装gunicorn：
   ```bash
   pip install gunicorn
   ```

2. 创建生产配置文件`config_prod.py`，设置`FLASK_ENV=production`，禁用调试。

3. 使用gunicorn启动：
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

4. 配置Nginx反向代理。

## 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启一个 Pull Request

请确保代码风格一致，并更新相关文档。

## 注意事项

- 本系统仅为健身辅助工具，不替代专业医疗或健身教练建议。
- 请根据自身身体状况调整训练强度，如有不适请立即停止。
- 定期备份数据库。

## 许可证

MIT