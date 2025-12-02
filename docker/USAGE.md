# LeanGain-AI Docker 镜像使用说明

## 1. 获取镜像

### 从 Docker Hub 拉取（如果已推送）

```bash
docker pull your-dockerhub-username/leangain-ai:latest
```

### 或从源码构建

```bash
git clone https://github.com/JackSuran/LeanGain-AI.git
cd LeanGain-AI/docker
docker build -t leangain-ai:latest -f Dockerfile ..
```

## 2. 运行容器

### 单容器运行（需要外部 MySQL）

应用需要连接 MySQL 数据库。您可以使用以下命令启动一个 MySQL 容器，然后启动应用容器。

#### 启动 MySQL

```bash
docker run -d \
  --name mysql-leangain \
  -e MYSQL_ROOT_PASSWORD=rootpassword \
  -e MYSQL_DATABASE=bodybuilding \
  -e MYSQL_USER=appuser \
  -e MYSQL_PASSWORD=apppassword \
  -p 3306:3306 \
  mysql:8.0
```

#### 启动应用容器

```bash
docker run -d \
  --name leangain-app \
  -p 5000:5000 \
  -e DATABASE_HOST=host.docker.internal  # Windows/macOS 用 host.docker.internal，Linux 用实际 IP
  -e DATABASE_USER=appuser \
  -e DATABASE_PASSWORD=apppassword \
  -e DATABASE_NAME=bodybuilding \
  -e SECRET_KEY=your-secret-key \
  -e DEEPSEEK_API_KEY=your-api-key \
  your-dockerhub-username/leangain-ai:latest
```

### 使用 Docker Compose（推荐）

在 `docker/` 目录下已有 `docker-compose.yml` 文件，它包含了 MySQL 和应用的完整编排。

1. 复制环境变量文件并配置：

```bash
cd docker
cp ../.env.example .env
# 编辑 .env 文件，设置 DEEPSEEK_API_KEY 等
# 注意：该文件已包含 Docker 和本地开发两套配置，请根据注释选择并填写
```

2. 启动服务：

```bash
docker-compose up -d
```

3. 查看日志：

```bash
docker-compose logs -f
```

4. 停止服务：

```bash
docker-compose down
```

## 3. 访问应用

- 应用地址：http://localhost:5000
- MySQL 地址：localhost:3306（用户：appuser，密码：apppassword）

## 4. 初始化数据库

首次访问时，数据库表可能尚未创建。您可以通过以下方式初始化：

- 访问 http://localhost:5000/initdb （自动创建表）
- 或手动执行 `create_database.py`（已在容器启动时自动运行）

## 5. 其他管理命令

- 查看运行中的容器：`docker-compose ps`
- 进入应用容器：`docker-compose exec app bash`
- 备份数据库：`docker-compose exec mysql mysqldump -u appuser -papppassword bodybuilding > backup.sql`

## 6. 自定义配置

您可以通过修改 `docker-compose.yml` 或 `.env` 文件来调整端口、数据库密码等设置。

## 7. 网络问题与镜像加速

如果在构建或拉取镜像时遇到网络错误（例如 `failed to resolve source metadata for docker.io/library/python:3.9-slim`），可以尝试以下解决方案：

### 使用 Alpine 镜像（已测试）
项目 Dockerfile 已默认使用 `python:3.9-alpine` 作为基础镜像，该镜像体积更小且通常更容易拉取。如果之前使用 `python:3.9-slim` 失败，请确保使用最新的 Dockerfile。

### 配置 Docker 镜像加速器
对于中国用户，可以配置 Docker 国内镜像加速器以提升拉取速度。

1. 编辑 Docker 配置文件（位于 `~/.docker/daemon.json` 或 `C:\ProgramData\Docker\config\daemon.json`），添加以下内容：
```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```
2. 重启 Docker 服务。

### 离线构建
如果完全无法访问外部网络，可以预先在有网络的环境中下载所需镜像，导出为 tar 文件，然后在离线环境中导入。

1. 在有网络的环境中拉取基础镜像：
```bash
docker pull python:3.9-alpine
docker pull mysql:8.0
```
2. 保存镜像：
```bash
docker save -o python-3.9-alpine.tar python:3.9-alpine
docker save -o mysql-8.0.tar mysql:8.0
```
3. 将 tar 文件传输到离线环境，并导入：
```bash
docker load -i python-3.9-alpine.tar
docker load -i mysql-8.0.tar
```
4. 然后正常构建应用镜像。

## 8. 故障排除

### 端口冲突
如果启动时出现类似 `ports are not available: exposing port TCP 0.0.0.0:3306 -> ... bind: Only one usage of each socket address ...` 的错误，说明端口已被占用。

**解决方案**：
1. **修改端口映射**：编辑 `docker-compose.yml`，将冲突的端口改为其他可用端口（例如将 `"3306:3306"` 改为 `"3307:3306"`，将 `"5000:5000"` 改为 `"5001:5000"`）。
2. **停止占用端口的进程**：
   - 查找占用端口的进程（例如 `netstat -ano | findstr :3306`）。
   - 根据进程ID（PID）决定是否停止该进程（如不需要本地 MySQL 服务，可通过服务管理器停止 MySQL）。
3. **使用不同的端口启动**：如果修改了端口，访问应用时需使用新端口（例如 MySQL 连接使用 `localhost:3307`）。

### 连接数据库失败
确保 MySQL 容器已启动且网络互通。在 Windows/macOS 上，使用 `host.docker.internal` 作为主机名；在 Linux 上，使用 Docker 网络别名 `mysql`（当使用 docker-compose 时）。

### API 密钥未设置
务必在 `.env` 文件中设置 `DEEPSEEK_API_KEY`。

### 构建时出现 `libmysqlclient.so` 错误
确保使用最新的 Dockerfile（已修复 Alpine 下的符号链接问题）。

更多帮助请参考项目 README。