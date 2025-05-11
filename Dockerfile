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
RUN uv pip install --system -e .

# 5. 暴露端口
EXPOSE 7001

# 6. 设置默认启动命令
# 使用shell格式的CMD，这样可以使用环境变量和进行检查
CMD echo "Starting MCP server..." && \
    if [ -z "${organizationId}" ]; then \
        echo "ERROR: Required environment variable 'organizationId' must be set."; \
        echo "Please run with: docker run --env-file .env -p 7001:7001 yx-mcp"; \
        tail -f /dev/null; \
    elif [ -z "${x_yunxiao_token}" ] && [ -z "${x-yunxiao-token}" ]; then \
        echo "ERROR: Required environment variable 'x-yunxiao-token' must be set."; \
        echo "Please run with: docker run --env-file .env -p 7001:7001 yx-mcp"; \
        tail -f /dev/null; \
    else \
        echo "DEBUG: Entering CMD else branch, about to execute uv run..." && \
        uv run mcp run mcp_server.py && \
        echo "DEBUG: uv run mcp run mcp_server.py command finished." && \
        tail -f /dev/null; \
    fi
