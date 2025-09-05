# UptimeGuard 应用镜像 Dockerfile
# 基于预构建的基础镜像，只复制应用代码
FROM uptimeguard-base:latest

# 设置工作目录
WORKDIR /app

# 复制项目文件到工作目录
COPY app.py .
COPY monitor.py .
COPY ui.py .
COPY storage.py .
COPY log_manager.py .
COPY docker_utils.py .
COPY telegram_config.py .
COPY telegram_notifier.py .
COPY telegram_chat_bot.py .
COPY start_chat_bot.py .
COPY status_check.py .

# 复制配置文件和依赖
COPY requirements.txt .
COPY sites.json .
COPY telegram_config.json .

# 创建必要的目录
RUN mkdir -p /app/logs

# 设置权限
RUN chmod +x app.py
RUN chmod +x start_chat_bot.py
RUN chmod +x status_check.py

# 设置 Python 路径，确保可以找到当前目录的模块
ENV PYTHONPATH=/app

# 设置环境变量
ENV DOCKER_RUN=true

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7863/ || exit 1

# 暴露端口
EXPOSE 7863

# 默认命令：运行 UptimeGuard 应用
CMD ["python", "app.py"]
