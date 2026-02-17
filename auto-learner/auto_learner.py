#!/usr/bin/env python3
"""
Auto-Learner - 自动学习器 v2

持续学习版本：在指定时间内循环学习
"""

import os
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import requests

# 配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
GITHUB_API = "https://api.github.com"
LEARNING_TOPICS = ["openclaw", "n8n", "dify", "automation", "ai-agent", 
                   "claude-code", "gemini-cli", "cursor", "langflow", "browser-use"]

def log(msg):
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    # 同时写入日志文件
    log_file = WORKSPACE / "learning" / "learning.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "a") as f:
        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")

def check_existing_skills():
    """自检现有skills"""
    skills_dir = Path.home() / ".openclaw" / "skills"
    skills = []
    for d in skills_dir.iterdir():
        if d.is_dir() and not d.name.startswith('.') and not d.is_symlink():
            skill_file = d / "SKILL.md"
            if skill_file.exists():
                skills.append({"name": d.name, "path": str(d)})
    log(f"🔍 自检: 发现 {len(skills)} 个Skills")
    return skills

def search_github(topic, per_page=10):
    """搜索GitHub"""
    try:
        url = f"{GITHUB_API}/search/repositories"
        params = {"q": topic, "sort": "stars", "order": "desc", "per_page": per_page}
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            items = []
            for item in data.get("items", [])[:5]:
                items.append({
                    "name": item.get("full_name", ""),
                    "desc": item.get("description", "")[:100],
                    "stars": item.get("stargazers_count", 0),
                    "url": item.get("html_url", ""),
                    "lang": item.get("language", "")
                })
            log(f"   📦 {topic}: {len(items)} 个项目")
            return items
    except Exception as e:
        log(f"   ❌ {topic} 搜索失败: {e}")
    return []

def learning_cycle(cycle_num):
    """单次学习循环"""
    log(f"📚 第{cycle_num}轮学习开始")
    
    # 1. 自检
    skills = check_existing_skills()
    
    # 2. 学习GitHub
    all_results = {}
    for topic in LEARNING_TOPICS:
        results = search_github(topic)
        if results:
            all_results[topic] = results
        time.sleep(1.5)  # 避免API限流
    
    # 3. 生成报告
    report = generate_report(skills, all_results, cycle_num)
    
    # 4. 保存报告
    save_report(report, cycle_num)
    
    log(f"✅ 第{cycle_num}轮学习完成")
    return True

def generate_report(skills, github_data, cycle_num):
    """生成学习报告"""
    report = f"""# 自动学习报告 - 第{cycle_num}轮

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 现有Skills ({len(skills)}个)

"""
    for s in skills:
        report += f"- {s['name']}\n"
    
    report += "\n## GitHub 学习成果\n\n"
    
    for topic, items in github_data.items():
        report += f"### {topic}\n\n"
        for item in items:
            report += f"- **{item['name']}** ⭐{item['stars']}\n"
            report += f"  - {item['desc']}\n"
            report += f"  - [链接]({item['url']})\n\n"
    
    return report

def save_report(report, cycle_num):
    """保存报告"""
    report_dir = WORKSPACE / "learning"
    report_dir.mkdir(parents=True, exist_ok=True)
    
    filename = report_dir / f"report_cycle{cycle_num}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    filename.write_text(report)
    log(f"📄 报告已保存: {filename}")

def auto_learn(hours=1):
    """自动学习主循环"""
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=hours)
    
    log(f"🚀 开始自动学习")
    log(f"   开始: {start_time.strftime('%H:%M:%S')}")
    log(f"   结束: {end_time.strftime('%H:%M:%S')}")
    
    cycle_num = 1
    while datetime.now() < end_time:
        learning_cycle(cycle_num)
        cycle_num += 1
        
        # 检查是否还有时间
        remaining = (end_time - datetime.now()).total_seconds()
        if remaining > 600:  # 还有10分钟以上
            log(f"⏳ 等待5分钟后继续...")
            time.sleep(300)  # 5分钟
        elif remaining > 60:
            log(f"⏳ 等待1分钟后继续...")
            time.sleep(60)
        else:
            break
    
    log(f"🎉 全部学习完成! 共{cycle_num-1}轮")

def main():
    import sys
    
    hours = 1.0
    if len(sys.argv) > 1:
        try:
            hours = float(sys.argv[1])
        except:
            pass
    
    print(f"""
🔧 Auto-Learner v2 - 自动学习器
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
学习时长: {hours}小时
学习主题: {len(LEARNING_TOPICS)}个
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    
    auto_learn(hours)

if __name__ == "__main__":
    main()
