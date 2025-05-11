# MCP Workitem Server

## 依赖安装
本项目推荐使用 [uv](https://github.com/astral-sh/uv) 进行依赖管理和运行。

<a href="https://glama.ai/mcp/servers/@tingxifa/mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@tingxifa/mcp/badge" alt="Workitem Server MCP server" />
</a>

### 安装 uv
```bash
pip install uv  # 或参考 uv 官方文档
```

### 安装依赖
```bash
uv pip install -r requirements.txt
```

## 环境变量与配置
- 推荐使用 `.env` 文件或环境变量注入敏感信息。
- 必需：
  - `organizationId`：阿里云组织ID
  - `x-yunxiao-token`：阿里云API Token

### .env 自动加载说明
- fastmcp 和 uv 支持自动加载项目根目录下的 `.env` 文件，无需额外代码。
- 启动服务时（如 `uv run mcp run mcp_server.py`），会自动读取 `.env` 文件中的变量。
- 你也可以用 [python-dotenv](https://github.com/theskumar/python-dotenv) 手动加载（如有特殊需求）。

### .env 示例文件
在项目根目录下新建 `.env` 文件，内容如下：
```
organizationId=your_org_id
x-yunxiao-token=your_token
```
- `.env` 文件用于本地开发和测试，**请勿提交敏感信息到代码仓库**。
- 建议在 `.gitignore` 文件中加入 `.env`，防止泄漏：
  ```
  # .gitignore
  .env
  ```

## Docker 部署与环境变量注入

### 构建镜像
```bash
docker build -t yx-mcp .
```

### 运行容器（推荐方式）
1. **通过 --env-file 挂载 .env 文件**
   - 在项目根目录准备好 `.env` 文件（内容同上）
   - 启动容器：
     ```bash
     docker run --env-file .env -p 9000:9000 yx-mcp
     ```
2. **通过 -e 传递环境变量**
   - 直接在命令行传递敏感信息：
     ```bash
     docker run -e organizationId=your_org_id -e x-yunxiao-token=your_token -p 9000:9000 yx-mcp
     ```
3. **通过 volume 挂载 .env 文件**
   - 将本地 .env 文件挂载到容器内：
     ```bash
     docker run -v $(pwd)/.env:/app/.env -p 9000:9000 yx-mcp
     ```

> **安全提示：** 不要将 `.env` 文件 COPY 进镜像，避免敏感信息泄漏。推荐用 `--env-file` 或 `-e` 方式传递。

## 启动服务
```bash
# 方式一：直接用环境变量
export organizationId=your_org_id
export x-yunxiao-token=your_token
uv run mcp run mcp_server.py

# 方式二：自动加载 .env 文件（推荐）
uv run mcp run mcp_server.py
```

## 工具说明
本服务通过 MCP 协议暴露 `get_workitem_description` 工具，参数为需求ID（如 YEPPPP-154），返回结构化 JSON，包含：
- `text`：纯文本描述
- `images`：图片 URL 列表
- `html`：原始 HTML 内容

### 返回示例
```json
{
  "id": "YEPPPP-154",
  "text": "需求描述文本...",
  "images": ["https://...jpg"],
  "html": "<div>...</div>"
}
```

## 错误处理
- 若外部 API 请求失败，返回 `{ "error": "错误信息" }`，agent 可据此判断。

## agent 调用建议
- 通过 MCP 协议自动发现和调用 `get_workitem_description` 工具。
- 仅需传入 `id` 参数，无需关心 org_id/token。

## 开发与调试
- 推荐用 `uv run fastmcp dev mcp_server.py` 进行本地开发，支持热重载和交互测试。
- 支持标准 MCP agent 生态。

## 参考
- [uv 官方文档](https://github.com/astral-sh/uv)
- [fastmcp 官方文档](https://gofastmcp.com/)
- [MCP 协议介绍](https://github.com/jlowin/fastmcp)
- [python-dotenv](https://github.com/theskumar/python-dotenv)