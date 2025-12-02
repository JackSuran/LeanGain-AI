#!/bin/bash
# LeanGain-AI Docker 镜像推送脚本
# 将镜像推送到 Docker Hub 或其它容器仓库

set -e

# 配置
IMAGE_NAME="leangain-ai"
TAG="latest"
REPOSITORY="your-dockerhub-username"  # 请替换为你的 Docker Hub 用户名

# 登录 Docker Hub（如果需要）
if [ "$1" = "--login" ]; then
    echo "请登录 Docker Hub..."
    docker login
fi

# 构建镜像
echo "构建镜像 ${IMAGE_NAME}:${TAG} ..."
docker build -t ${IMAGE_NAME}:${TAG} -f Dockerfile ..

# 标记为远程仓库
REMOTE_IMAGE="${REPOSITORY}/${IMAGE_NAME}:${TAG}"
echo "标记为 ${REMOTE_IMAGE} ..."
docker tag ${IMAGE_NAME}:${TAG} ${REMOTE_IMAGE}

# 推送
echo "推送镜像到 ${REMOTE_IMAGE} ..."
docker push ${REMOTE_IMAGE}

echo "推送完成。"
echo "其他人可以使用以下命令拉取镜像："
echo "  docker pull ${REMOTE_IMAGE}"