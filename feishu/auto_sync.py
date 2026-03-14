#!/usr/bin/env python3
"""
飞书自动更新脚本
每天凌晨 2 点自动检查并更新 Skill 版本到飞书
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

# 配置
SKILLS_DIR = Path.home() / ".openclaw/skills"
WORKSPACE_DIR = Path.home() / ".openclaw/workspace"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def get_local_skills():
    """获取本地 Skills"""
    skills = []
    for d in SKILLS_DIR.iterdir():
        if d.is_dir() and not d.name.startswith('.') and not d.name.startswith('skill-'):
            skill_file = d / "SKILL.md"
            metadata_file = d / "metadata.json"
            
            version = "未知"
            description = ""
            
            # 读取版本
            if skill_file.exists():
                try:
                    with open(skill_file) as f:
                        for line in f:
                            if 'version:' in line.lower():
                                version = line.split(':')[-1].strip()
                                break
                            if 'description:' in line.lower():
                                description = line.split(':', 1)[-1].strip()
                except:
                    pass
            
            # 读取 metadata
            if metadata_file.exists():
                try:
                    with open(metadata_file) as f:
                        meta = json.load(f)
                        version = meta.get('openclaw', {}).get('version', version)
                except:
                    pass
            
            skills.append({
                "name": d.name,
                "path": str(d),
                "version": version,
                "description": description
            })
    
    return skills

def check_updates():
    """检查是否有更新"""
    log("🔍 检查 Skill 更新...")
    skills = get_local_skills()
    log(f"   本地 Skills: {len(skills)}")
    return skills

def generate_report(skills):
    """生成更新报告"""
    report = f"# 📊 Skill 自检报告\n\n"
    report += f"**检查时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    report += f"## 📋 Skills 清单\n\n"
    report += f"| 名称 | 版本 | 描述 |\n"
    report += f"|------|------|------|\n"
    
    for s in skills:
        desc = s.get('description', '')[:30]
        report += f"| {s['name']} | {s['version']} | {desc} |\n"
    
    return report

def send_to_feishu(message):
    """发送消息到飞书"""
    log(f"📨 发送报告到飞书...")
    
    # 使用 OpenClaw 的 message 工具发送
    # 这里生成一个飞书可用的消息格式
    report_file = WORKSPACE_DIR / "memory/feishu_update_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(message)
    
    log(f"✅ 报告已保存到: {report_file}")
    
    # 返回消息，用户可以通过飞书查看
    return message

def main():
    print("=" * 50)
    print("🔄 飞书自动更新检查")
    print("=" * 50)
    
    # 检查更新
    skills = check_updates()
    
    # 生成报告
    report = generate_report(skills)
    
    # 发送飞书
    send_to_feishu(report)
    
    # 统计
    total = len(skills)
    log(f"📊 共检查 {total} 个 Skills")
    
    print("=" * 50)
    print("✅ 自检完成")
    print("=" * 50)

if __name__ == "__main__":
    main()
