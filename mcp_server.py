import os
from pprint import pprint

# 自动加载.env文件（如果存在）
from dotenv import load_dotenv
from mcp import ServerSession

load_dotenv()
import json
import re
import html
import requests
from fastmcp import FastMCP
from typing import Annotated
from pydantic import Field


old__received_request = ServerSession._received_request


async def _received_request(self, *args, **kwargs):
    try:
        return await old__received_request(self, *args, **kwargs)
    except RuntimeError:
        pass


# pylint: disable-next=protected-access
ServerSession._received_request = _received_request


mcp = FastMCP("workitem-mcp-server", log_level="INFO")

def extract_content_and_image_urls_from_html(html_value):
    images = []
    def replace_img_with_placeholder(match):
        src_match = re.search(r'src=(["\'])(.*?)\1', match.group(0), re.IGNORECASE)
        if src_match:
            url = src_match.group(2)
            placeholder = f"__IMAGE_URL_{len(images)}__"
            images.append(url)
            return placeholder
        return ""
    html_value_with_placeholders = re.sub(r"<img[^>]*>", replace_img_with_placeholder, html_value, flags=re.IGNORECASE | re.DOTALL)
    text_only = re.sub(r"<[^>]+>", "", html_value_with_placeholders)
    text_only = html.unescape(text_only)
    for i, url in enumerate(images):
        placeholder = f"__IMAGE_URL_{i}__"
        text_only = text_only.replace(placeholder, f"\nImage URL: {url}\n")
    cleaned_text = re.sub(r'\n\s*\n', '\n', text_only)
    lines = [line.strip() for line in cleaned_text.split('\n') if line.strip()]
    return "\n".join(lines), images

@mcp.tool(description="通过需求 ID 获取需求详情")
def get_work_item_description(
        id: Annotated[
            str,
            Field(
                description="需求ID，必须以 YEPPPP 开头，如 YEPPPP-154",
                pattern="^YEPPPP.*"
            )
        ]
) -> dict:
    """
    获取需求描述，返回结构化 JSON，包含纯文本、图片 URL、原始 HTML
    """
    org_id = os.environ.get("organizationId")
    token = os.environ.get("x-yunxiao-token")
    if not org_id or not token:
        raise RuntimeError("环境变量 organizationId 和 x-yunxiao-token 必须设置")
    url = f"https://openapi-rdc.aliyuncs.com/oapi/v1/projex/organizations/{org_id}/workitems/{id}"
    headers = {"x-yunxiao-token": token}
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        description = data['description']
        json_data = json.loads(description)
        html_value = json_data['htmlValue']
        text, images = extract_content_and_image_urls_from_html(html_value)
        tishi = """
        这里有一个需求，你需要执行如下步骤， 但只需要输出后端详细的功能点， 用于指导开发：
1. 识别文本与图片内容，进行内容识别
2. 结合文本与图片的内容，将内容合并进行梳理成详细的功能点， 可以进行额外补充，但是提供在建议内
3. 检查功能点是否完善与详细

        """
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        if not gemini_api_key:
            raise RuntimeError("环境变量 GEMINI_API_KEY 必须设置")
        gemini_model = os.environ.get("GEMINI_MODEL")
        if not gemini_model:
            raise RuntimeError("环境变量 GEMINI_MODEL 必须设置")
        base_url = os.environ.get("GEMINI_BASE_URL")
        if not base_url:
            base_url = "https://generativelanguage.googleapis.com/v1beta"
        url = f"{base_url}/models/{gemini_model}:generateContent?key={gemini_api_key}"

        resp = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": tishi + text}]}]}
        )
        resp.raise_for_status()
        data = resp.json()
        candidates_ = data['candidates']
        content_ = candidates_[0]['content']
        parts_ = content_['parts']
        # 遍历累加 text
        text_ = ""
        for part in parts_:
            text_ += part['text']

        return {
            "id": id,
            "text": text_,
            "images": images,
            # "html": html_value
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("DEBUG: About to call mcp.run()")
    mcp.run(transport="sse", host="0.0.0.0", port=7001)
    print("DEBUG: mcp.run() finished or was bypassed")
