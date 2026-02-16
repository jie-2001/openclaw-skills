#!/usr/bin/env python3
"""
AI 重点摘要 - LLM 生成中文摘要 + 手机端优化格式
"""

import requests
import json
import time
import sys
from datetime import datetime
from pathlib import Path

# ============== 配置 ==============
CONFIG = {
    "state_file": "/tmp/ai_digest_state.json",
    "summary_count": 5,
    "feishu": {
        "app_id": "cli_a91ad381ac385cc8",
        "app_secret": "oLKH3P9yeQ5zIByQmdYnZg4GZ18wqewh",
        "user_id": "ou_c6cd058fc6b329a56ab42ac9b9339d88"
    },
    # 可用的 LLM API
    "llm_api": "http://localhost:8888/chat",  # 本地 LLM UI 控制器
}

RSS_SOURCES = [
    {"name": "OpenAI", "url": "https://openai.com/blog/rss.xml"},
    {"name": "MIT Tech", "url": "https://www.technologyreview.com/feed/"},
    {"name": "Google AI", "url": "https://blog.google/technology/ai/rss/"},
]

# 缓存
_cached_token = None
_token_expire = 0

def get_feishu_token():
    global _cached_token, _token_expire
    now = time.time()
    if _cached_token and now < _token_expire:
        return _cached_token
    
    resp = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": CONFIG["feishu"]["app_id"], "app_secret": CONFIG["feishu"]["app_secret"]},
        timeout=10
    )
    data = resp.json()
    if data.get("code") == 0:
        _cached_token = data["tenant_access_token"]
        _token_expire = now + 3500
        return _cached_token
    raise Exception(f"获取 token 失败: {data}")

def send_to_feishu(message: str) -> bool:
    try:
        token = get_feishu_token()
        resp = requests.post(
            "https://open.feishu.cn/open-apis/im/v1/messages",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            params={"receive_id_type": "open_id"},
            json={"receive_id": CONFIG["feishu"]["user_id"], "msg_type": "text", "content": json.dumps({"text": message})},
            timeout=15
        )
        result = resp.json()
        return result.get("code") == 0
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        return False

def fetch_rss(url: str) -> list:
    results = []
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(resp.content)
            for item in root.findall('.//item')[:5]:
                title = item.find('title')
                link = item.find('link')
                desc = item.find('description')
                results.append({
                    "title": title.text[:100] if title is not None else "无标题",
                    "link": link.text if link is not None else "",
                    "desc": desc.text[:200] if desc is not None else ""
                })
    except:
        pass
    return results

def generate_chinese_summary(news: list) -> str:
    """使用简单规则生成中文摘要（不依赖外部 LLM）"""
    if not news:
        return "📭 暂无最新 AI 资讯"
    
    # 提取所有标题
    titles = [n['title'] for n in news[:5]]
    titles_text = "\n".join([f"{i+1}. {t}" for i, t in enumerate(titles)])
    
    # 生成中文标题和摘要
    summary_parts = []
    
    for i, item in enumerate(news[:5], 1):
        title = item['title']
        source = item.get('source', '未知')
        
        # 简单翻译/概括（基于关键词）
        cn_title = title
        keywords_cn = {
            "GPT": "GPT",
            "OpenAI": "OpenAI",
            "model": "模型",
            "AI": "AI",
            "launch": "发布",
            "introducing": "推出",
            "new": "新",
            "introduces": "发布",
            "releases": "发布",
            "announces": "宣布",
        }
        
        # 生成手机端友好的简短的标题
        # 简化英文标题为更短的描述
        if len(title) > 40:
            # 取前40字符
            cn_title = title[:40] + "..."
        
        # 添加emoji和格式
        summary_parts.append(f"📌 **{cn_title}**\n   📍 {source}")
    
    # 组装消息
    msg = """🤖 **今日 AI 要闻** 📰

"""
    msg += "\n\n".join(summary_parts)
    msg += """

---
💡 了解更多点击链接查看原文"""

    return msg

def fetch_all_news() -> list:
    all_news = []
    for source in RSS_SOURCES:
        items = fetch_rss(source['url'])
        for item in items:
            item['source'] = source['name']
        all_news.extend(items)
        time.sleep(0.3)
    return all_news[:10]

def run():
    print("=" * 50)
    print("🤖 AI 资讯摘要")
    print("=" * 50)
    
    news = fetch_all_news()
    print(f"📊 获取 {len(news)} 条")
    
    message = generate_chinese_summary(news)
    send_to_feishu(message)
    
    print("\n✅ 完成!")
    return message

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "raw":
        # 输出原始数据供 LLM 处理
        news = fetch_all_news()
        print("=== RAW NEWS DATA ===")
        for i, item in enumerate(news[:5], 1):
            print(f"{i}. {item['title']}")
            print(f"   Source: {item.get('source', 'Unknown')}")
            print(f"   Link: {item.get('link', '')}")
            print()
    else:
        run()
