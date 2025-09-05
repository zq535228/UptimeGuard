#!/bin/bash

# UptimeGuard Docker 构建脚本
# 用于构建基础镜像和应用镜像

set -e  # 遇到错误立即退出

echo "🚀 开始构建 UptimeGuard Docker 镜像..."

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ 错误：Docker 未运行，请先启动 Docker"
    exit 1
fi

# 检查必要文件是否存在
echo "🔍 检查必要文件..."
required_files=("app.py" "monitor.py" "ui.py" "storage.py" "requirements.txt" "sites.json")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ 错误：缺少必要文件 $file"
        exit 1
    fi
done
echo "✅ 所有必要文件检查通过"

# 构建基础镜像（包含所有依赖）
echo "📦 构建基础镜像（包含系统依赖和 Python 包）..."
docker build -f Dockerfile.base -t uptimeguard-base:latest .

if [ $? -eq 0 ]; then
    echo "✅ 基础镜像构建成功！"
else
    echo "❌ 基础镜像构建失败！"
    exit 1
fi

# 构建应用镜像（基于基础镜像）
echo "📦 构建应用镜像（基于基础镜像）..."
docker build -f Dockerfile -t uptimeguard-app:latest .

if [ $? -eq 0 ]; then
    echo "✅ 应用镜像构建成功！"
else
    echo "❌ 应用镜像构建失败！"
    exit 1
fi

echo ""
echo "🎉 所有镜像构建完成！"
echo ""
echo "📋 可用的镜像："
echo "  - uptimeguard-base:latest  (基础镜像，包含所有依赖)"
echo "  - uptimeguard-app:latest   (应用镜像，包含应用代码)"
echo ""
echo "🚀 运行应用："
echo "  docker run -d \\"
echo "    --name uptimeguard \\"
echo "    -p 7863:7863 \\"
echo "    -v \$(pwd)/sites.json:/app/sites.json \\"
echo "    -v \$(pwd)/telegram_config.json:/app/telegram_config.json \\"
echo "    -v \$(pwd)/logs:/app/logs \\"
echo "    uptimeguard-app:latest"
echo ""
echo "🔧 或者使用 docker-compose："
echo "  docker-compose up -d uptimeguard"
echo ""
echo "🌐 访问地址："
echo "  http://localhost:7863"
