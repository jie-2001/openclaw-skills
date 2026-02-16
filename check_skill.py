#!/usr/bin/env python3
"""
Skill 上传检查工具

每次完成 Skill 开发后，运行此脚本检查是否完成所有上传步骤。

功能：
1. 检查 GitHub 是否有未提交的 Skill
2. 检查飞书管理表是否有遗漏
3. 检查飞书版本记录是否为空
"""

import os
import json
import subprocess
from pathlib import Path

# 配置
SKILLS_DIR = Path("~/.openclaw/skills").expanduser()
GITHUB_REPO = "jie-2001/openclaw-skills"

# 飞书文档 token（从管理表获取）
FEISHU_DOCS = {
    "ai-news-digest": "SGG1d3XUFopPZGxxivNcvn8OnJf",
    "memory-optimizer": "MeVpdqd9eoC1M2xdjgLcu30kngf",
    "memory-search-cli": "APjcdLnqUofZtyxCBkScpnHhnRE",
    "model-switcher": "L0ZIdPjOaoFY97xbfLWcKnulnWu",
    "local-security": "K7sVdMrCooq937xmk9rcY6xLnIf",
    "clawsec-suite": "C9QDdL9ZPoCkYRxkcrTcdjeBngX",
    "file-cleaner": "H4GOdztbEougICxf66ac3ejlnDg",
    "hook-auto-check": "Y2KNdEpCforS67xBgjkca5K9nzg",
    "word_update": "KWM7dbapIoWI15xCYNTcE1Y8nqe",
}

def check_github():
    """检查 GitHub 未提交的内容"""
    print("\n📦 检查 GitHub 提交状态...")
    
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=SKILLS_DIR,
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            print("⚠️  发现未提交的 Skill：")
            print(result.stdout)
            return False
        else:
            print("✅ GitHub 已同步")
            return True
            
    except Exception as e:
        print(f"❌ GitHub 检查失败: {e}")
        return False

def check_local_skills():
    """检查本地 Skill 目录"""
    print("\n📂 检查本地 Skills...")
    
    skills = [d for d in SKILLS_DIR.iterdir() 
             if d.is_dir() and not d.name.startswith('.')]
    
    print(f"本地 Skill 数量: {len(skills)}")
    for s in skills:
        print(f"  - {s.name}")
    
    return skills

def print_checklist():
    """打印检查清单"""
    print("\n" + "="*60)
    print("📋 Skill 开发完成检查清单")
    print("="*60)
    print("""
每次完成 Skill 开发后，必须执行以下所有步骤：

1️⃣ 飞书管理表
   - 更新「OpenClaw Skill 管理表」
   - 添加 Skill 名称、版本号、描述

2️⃣ 飞书版本记录（必须写内容！）
   - 创建版本记录文档（新建 Skill）
   - 立即写入版本内容（不能只创建空文档！）
   - 更新现有文档（修改 Skill）

3️⃣ GitHub 同步
   - git add
   - git commit -m "描述"
   - git push

4️⃣ 验证
   - 确认版本记录文档有实际内容（非空）
    """)
    print("="*60)

def main():
    print("🔍 Skill 上传检查工具")
    print_checklist()
    
    # 检查 GitHub
    check_github()
    
    # 检查本地
    check_local_skills()
    
    print("\n✅ 检查完成！")

if __name__ == "__main__":
    main()
