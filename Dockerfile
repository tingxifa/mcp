FROM python:3.10-slim

# 1. 安装 uv 工具
RUN pip install --no-cache-dir uv

# 2. 设置工作目录
WORKDIR /app

# 3. 复制项目文件（不包含 .env）
COPY . /app

# 4. 安装依赖（基于 pyproject.toml）
RUN uv pip install .

# 5. 暴露端口
EXPOSE 7001

# 6. 设置默认启动命令
CMD ["uv", "run", "mcp", "run", "mcp_server.py"] 