#!/bin/bash

# UptimeGuard Docker 自动构建和运行脚本
# 停止现有容器，重新构建镜像，然后启动新容器

set -e  # 遇到错误立即退出

echo "🔄 UptimeGuard Docker 自动构建和运行脚本"
echo "=========================================="

# 停止并删除现有容器
echo "🛑 停止现有容器..."
docker compose down || true

# 删除现有镜像（可选，强制重新构建）
echo "🗑️  删除现有镜像..."
docker rmi uptimeguard-app:latest || true
docker rmi uptimeguard-base:latest || true

# 重新构建镜像（无缓存）
echo "🔨 重新构建镜像（无缓存）..."
docker build --no-cache -f Dockerfile.base -t uptimeguard-base:latest .
docker build --no-cache -f Dockerfile -t uptimeguard-app:latest .

# 启动新容器
echo "🚀 启动新容器..."
docker compose up -d

# 等待容器启动
echo "⏳ 等待容器启动..."
sleep 10

# 检查容器状态
echo "📊 检查容器状态..."
docker compose ps

# 显示日志
echo "📝 显示最新日志..."
docker compose logs --tail=20 uptimeguard

echo ""
echo "✅ 部署完成！"
echo "🌐 访问地址：http://localhost:7863"
echo "📋 查看日志：docker compose logs -f uptimeguard"
echo "🛑 停止服务：docker compose down"