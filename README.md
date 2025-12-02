# LeanGain AI - 瘦子增重增肌智能健身系统

一个基于Flask + PyMySQL + DeepSeek AI的个人健身计划系统，专为瘦子（外胚型）设计，帮助用户科学增重增肌。利用AI生成个性化训练计划，跟踪进度，实现智能健身。

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
├── docker/               # Docker相关文件
│   ├── Dockerfile        # 应用镜像定义
│   ├── docker-compose.yml # 多服务编排
│   ├── push_image.sh     # 镜像推送脚本
│   ├── docker-start.sh   # 快速启动脚本
│   └── USAGE.md          # Docker使用说明
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
git clone https://github.com/JackSuran/LeanGain-AI.git
cd LeanGain-AI
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
DATABASE_NAME=leangain_ai
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

### 5. 初始化数据库

确保MySQL服务运行，并创建数据库：

```sql
CREATE DATABASE leangain_ai;
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

### 7. 使用 Docker 运行（推荐）

项目已提供完整的 Docker 支持，可以快速启动包含 MySQL 和 Flask 应用的完整环境。

#### 使用 Docker Compose

1. 确保已安装 [Docker](https://docs.docker.com/get-docker/) 和 [Docker Compose](https://docs.docker.com/compose/install/)。

2. 进入项目目录，复制环境变量文件并配置：

```bash
cd docker
cp ../.env.example .env
# 编辑 .env 文件，设置 DEEPSEEK_API_KEY 等（注意根据 Docker 环境调整 DATABASE_HOST 等变量）
```

3. 启动服务：

```bash
docker-compose up -d
```

4. 访问应用：http://localhost:5000

5. 停止服务：

```bash
docker-compose down
```

更多详细说明请参阅 [docker/USAGE.md](docker/USAGE.md)。

#### 网络问题解决

如果在构建镜像时遇到 `python:3.9-slim` 拉取失败（网络问题），项目已改用 `python:3.9-alpine` 作为基础镜像，该镜像更小且更容易拉取。如果仍遇到网络问题，可以尝试以下方法：

- **配置 Docker 镜像加速器**：编辑 Docker 配置文件（`daemon.json`）添加国内镜像源，如 `https://docker.mirrors.ustc.edu.cn`。
- **离线构建**：预先在有网络的环境中拉取 `python:3.9-alpine` 和 `mysql:8.0` 镜像，导出为 tar 文件，然后在离线环境中导入。

详细步骤请参阅 [docker/USAGE.md](docker/USAGE.md) 中的“网络问题与镜像加速”章节。

#### 构建自定义镜像

如果你想将镜像推送到自己的容器仓库，可以使用提供的脚本：

```bash
cd docker
./push_image.sh --login
```

#### 直接使用 Docker 运行单个容器

如果你已有 MySQL 服务，可以单独运行应用容器：

```bash
docker run -d \
  --name leangain-app \
  -p 5000:5000 \
  -e DATABASE_HOST=host.docker.internal \
  -e DATABASE_USER=appuser \
  -e DATABASE_PASSWORD=apppassword \
  -e DATABASE_NAME=leangain_ai \
  -e SECRET_KEY=your-secret-key \
  -e DEEPSEEK_API_KEY=your-api-key \
  your-dockerhub-username/leangain-ai:latest
```

### 8. 使用流程

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
- 数据库`leangain_ai`是否存在

### DeepSeek API

你需要注册DeepSeek平台并获取API密钥。将密钥填入`.env`的`DEEPSEEK_API_KEY`。

如果无法访问DeepSeek，系统会使用默认计划（模拟数据）。

## 故障排除

遇到问题？请查阅 [FIX_LOG.md](FIX_LOG.md) 获取常见问题与修复方案。

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