#!/usr/bin/env python3
"""
Auto-Learner - 自动学习器

功能：
1. 自检现有skills
2. 从GitHub学习openclaw/n8n/dify相关内容
3. 整理成飞书学习资料
4. 自动运行，无需询问
"""

import os
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import webbrowser
import requests

# 配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
GITHUB_API = "https://api.github.com"
LEARNING_TOPICS = ["openclaw", "n8n", "dify", "automation", "ai-agent"]

def log(msg):
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def check_existing_skills():
    """自检现有skills"""
    log("🔍 自检现有Skills...")
    skills_dir = Path.home() / ".openclaw" / "skills"
    skills = []
    for d in skills_dir.iterdir():
        if d.is_dir() and not d.name.startswith('.'):
            skill_file = d / "SKILL.md"
            if skill_file.exists():
                skills.append({"name": d.name, "path": str(d)})
    log(f"   现有 {len(skills)} 个Skills")
    return skills

def search_github(topic, per_page=10):
    """搜索GitHub"""
    log(f"🔎 搜索 GitHub: {topic}")
    try:
        url = f"{GITHUB_API}/search/repositories"
        params = {"q": topic, "sort": "stars", "order": "desc", "per_page": per_page}
        resp = requests.get(url, params=params, timeout=10)
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
            log(f"   找到 {len(items)} 个相关项目")
            return items
    except Exception as e:
        log(f"   搜索失败: {e}")
    return []

def fetch_readme(url):
    """获取README内容"""
    try:
        # 转换URL获取raw内容
        raw_url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        resp = requests.get(raw_url, timeout=10)
        if resp.status_code == 200:
            return resp.text[:3000]  # 限制长度
    except:
        pass
    return ""

def analyze_skill_quality(skill_path):
    """分析skill质量"""
    results = {"has_script": False, "has_skill_md": False, "files": []}
    skill_path = Path(skill_path)
    
    # 检查文件
    for f in skill_path.iterdir():
        if f.is_file():
            results["files"].append(f.name)
            if f.suffix == ".py":
                results["has_script"] = True
            if f.name == "SKILL.md":
                results["has_skill_md"] = True
    
    return results

def suggest_improvements(skills):
    """基于现有skills给出优化建议"""
    suggestions = []
    
    # 统计
    with_script = sum(1 for s in skills if analyze_skill_quality(s["path"]).get("has_script"))
    without_script = len(skills) - with_script
    
    if without_script > 0:
        suggestions.append(f"建议: {without_script}个skill没有Python脚本，可考虑添加以增强功能")
    
    return suggestions

def auto_learn(hours=1):
    """自动学习主循环"""
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=hours)
    
    log(f"🚀 开始自动学习 (目标: {hours}小时)")
    log(f"   结束时间: {end_time.strftime('%H:%M:%S')}")
    
    # 步骤1: 自检现有skills
    skills = check_existing_skills()
    suggestions = suggest_improvements(skills)
    for s in suggestions:
        log(f"   💡 {s}")
    
    # 步骤2: 学习GitHub
    all_results = {}
    for topic in LEARNING_TOPICS:
        if datetime.now() >= end_time:
            break
        results = search_github(topic)
        if results:
            all_results[topic] = results
        time.sleep(1)  # 避免API限流
    
    # 步骤3: 生成报告
    report = generate_report(skills, all_results)
    
    log("📝 生成学习报告...")
    
    return report

def generate_report(skills, github_data):
    """生成学习报告"""
    report = f"""# 自动学习报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 现有Skills分析

| 名称 | 路径 |
|------|------|
"""
    for s in skills:
        report += f"| {s['name']} | {s['path']} |\n"
    
    report += f"\n**总计**: {len(skills)} 个Skills\n"
    
    report += "\n## GitHub 学习成果\n\n"
    
    for topic, items in github_data.items():
        report += f"### {topic}\n\n"
        for item in items:
            report += f"- **{item['name']}** ({item['stars']}⭐)\n"
            report += f"  - {item['desc']}\n"
            report += f"  - 🔗 {item['url']}\n\n"
    
    report += """
---

## 建议

1. 定期运行此学习器更新知识库
2. 将高星项目加入观察列表
3. 考虑fork有价值的项目
"""
    
    return report

def save_report(report):
    """保存报告"""
    report_dir = WORKSPACE / "learning"
    report_dir.mkdir(parents=True, exist_ok=True)
    
    filename = report_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    filename.write_text(report)
    log(f"📄 报告已保存: {filename}")
    return filename

def main():
    import sys
    
    # 默认学习1小时
    hours = 1
    if len(sys.argv) > 1:
        try:
            hours = int(sys.argv[1])
        except:
            pass
    
    print(f"""
🔧 Auto-Learner - 自动学习器
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
学习目标: {hours}小时
学习主题: {', '.join(LEARNING_TOPICS)}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    
    # 执行学习
    report = auto_learn(hours)
    
    # 保存报告
    report_file = save_report(report)
    
    # 输出报告
    print("\n" + "="*50)
    print(report)
    print("="*50)
    
    log("✅ 学习完成!")

if __name__ == "__main__":
    main()
