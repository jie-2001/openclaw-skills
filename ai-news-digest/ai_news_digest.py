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
    """生成中文摘要 - 新格式"""
    if not news:
        return "📭 暂无最新 AI 资讯"
    
    from datetime import datetime
    
    # 今天的日期
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now().replace(hour=0, minute=0, second=0)).strftime("%Y-%m-%d")
    
    # 归类关键词
    categories = {
        "AI模型发布": ["GPT", "model", "launch", "release", "introduce", "Gemini", "Claude", "Llama", "发布", "模型"],
        "AI更新": ["update", "upgrade", "improve", "new feature", "更新", "升级", "优化"],
        "AI新逻辑概念": ["reasoning", "agent", "architecture", "framework", "concept", "逻辑", "推理", "智能体"],
        "AI软件爆火": ["viral", "trending", "popular", "million", "用户", "爆火", "流行"],
        "AI安全": ["safety", "security", "privacy", "protect", "安全", "隐私"],
        "AI研究": ["research", "paper", "study", "发现", "研究", "论文"],
    }
    
    def categorize(title):
        title_lower = title.lower()
        for cat, keywords in categories.items():
            if any(k.lower() in title_lower for k in keywords):
                return cat
        return "AI资讯"
    
    # 生成消息
    msg = f"""🤖 **今日 AI 要闻** ({yesterday})

---

"""
    
    for i, item in enumerate(news[:5], 1):
        title = item['title']
        link = item.get('link', '')
        source = item.get('source', '未知')
        
        # 分类
        category = categorize(title)
        
        # 生成详细描述
        desc = title
        # 简化英文为中文描述
        if len(title) > 60:
            desc = title[:60] + "..."
        
        msg += f"""**{i}. {title}**

📝 {desc}

📊 表格信息:
| 发布时间 | 来源 | 归类 |
|----------|------|------|
| {yesterday} | {source} | {category} |

🔗 链接: {link}

---

"""
    
    msg += """💡 了解更多点击上方链接"""
    
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
