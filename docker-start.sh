#!/bin/bash
# LeanGain-AI Docker 启动脚本

set -e

echo "=== LeanGain-AI Docker 启动 ==="

# 检查是否已安装 Docker 和 Docker Compose
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装。请先安装 Docker。"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker Compose 未安装。请先安装 Docker Compose。"
    exit 1
fi

# 进入 docker 目录
cd docker

# 检查 .env 文件（在 docker 目录）
if [ ! -f .env ]; then
    if [ -f ../.env.example ]; then
        echo "警告: 未找到 .env 文件。将使用 ../.env.example 创建 .env 文件。"
        cp ../.env.example .env
        echo "请编辑 .env 文件，设置您的配置（尤其是 DEEPSEEK_API_KEY）。"
        read -p "是否现在编辑 .env 文件？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-vi} .env
        fi
    else
        echo "错误: 未找到 ../.env.example 文件。"
        exit 1
    fi
fi

# 构建并启动服务
echo "正在构建 Docker 镜像..."
docker-compose build

echo "正在启动服务..."
docker-compose up -d

echo "等待 MySQL 准备就绪..."
sleep 10

echo "=== 启动完成 ==="
echo "应用运行在 http://localhost:5000"
echo "MySQL 运行在 localhost:3307"
echo ""
echo "查看日志: docker-compose logs -f"
echo "停止服务: docker-compose down"
echo ""
echo "初始化数据库（如果需要）:"
echo "  访问 http://localhost:5000/initdb 创建表"