FROM python:3.10-slim

# 1. 安装 uv 工具
RUN pip install --no-cache-dir uv

# 2. 设置工作目录
WORKDIR /app

# 3. 复制项目文件（不包含 .env）
COPY . /app

# 4. 创建虚拟环境并安装依赖
RUN uv venv .venv
ENV PATH="/app/.venv/bin:$PATH"
RUN uv pip install -r pyproject.toml

# 5. 暴露端口
EXPOSE 7000

# 6. 设置默认启动命令
CMD ["python", "mcp_server.py"] 
