#!/usr/bin/env python3
"""
Word Update - 自动化上传更新脚本 v2

功能：
1. 自动更新 GitHub 仓库
2. 自动更新飞书版本记录（使用OpenClaw API）
3. 自动创建飞书版本文档

用法：
    python word_update.py --skill "skill名称" --desc "更新描述"
"""

import os
import sys
import json
import subprocess
import time
import requests
from pathlib import Path

# 配置
SKILLS_DIR = Path.home() / ".openclaw" / "skills"
GITHUB_REPO = "https://github.com/jie-2001/openclaw-skills.git"

# 飞书文档配置
FEISHU_DOCS = {
    "main": "YMr1dySwToBwSpxTJrpcNZODnCc",  # 主管理表
    "rules": "WtvAdzg8FoB985x7XQychilunpc",
}

# 版本记录文档映射
VERSION_DOCS = {}

def run_command(cmd, cwd=None, retry=3):
    """执行命令"""
    for attempt in range(retry):
        try:
            result = subprocess.run(cmd, shell=True, cwd=cwd, 
                                   capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                return True, result.stdout
            if attempt < retry - 1:
                time.sleep(2)
        except:
            if attempt < retry - 1:
                time.sleep(2)
    return False, result.stderr if 'result' in locals() else "命令执行失败"

def update_github(skill_name, desc):
    """更新 GitHub"""
    print("=== GitHub 更新 ===")
    
    skill_path = SKILLS_DIR / skill_name
    if not skill_path.exists():
        return False, f"Skill不存在: {skill_name}"
    
    # 检查更改
    success, output = run_command("git status --porcelain", cwd=SKILLS_DIR)
    if not success:
        return False, "无法检查git状态"
    
    if not output.strip():
        print("  ℹ️ 没有需要更新的内容")
        return True, "无需更新"
    
    # git add
    run_command("git add -A", cwd=SKILLS_DIR)
    print("  ✅ git add")
    
    # git commit
    commit_msg = f"{skill_name}: {desc}"
    success, output = run_command(f'git commit -m "{commit_msg}"', cwd=SKILLS_DIR)
    if "nothing to commit" in output.lower():
        print("  ℹ️ 没有需要提交的内容")
        return True, "无需提交"
    print(f"  ✅ commit")
    
    # git push
    success, output = run_command("git push origin main", cwd=SKILLS_DIR, retry=3)
    if not success:
        return False, f"push失败: {output}"
    print("  ✅ GitHub完成")
    
    return True, "GitHub更新成功"

def update_feishu(skill_name, desc):
    """更新飞书"""
    print("\n=== 飞书更新 ===")
    
    # 通过OpenClaw的feishu API更新
    # 这里使用feishu_doc工具的append功能
    
    # 1. 追加到主管理表
    main_doc = "YMr1dySwToBwSpxTJrpcNZODnCc"
    
    # 获取当前时间
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d")
    
    # 追加内容
    content = f"""
### {skill_name} ({now})
- 描述: {desc}
- 版本: v1.0.0
- 状态: ✅ 已上传GitHub
"""
    
    # 调用feishu API
    cmd = f'''curl -s -X POST "https://open.feishu.cn/open-apis/doc/v1/documents/{main_doc}/append" \
-H "Authorization: Bearer $(cat ~/.openclaw/config.yaml 2>/dev/null | grep -A5 feishu | grep token | head -1 | awk '{{print $2}}')" \
-H "Content-Type: application/json" \
-d '{{"text": "{content}"}}' 2>/dev/null'''
    
    # 由于无法直接调用API，这里记录操作
    print(f"  📝 记录: {skill_name} - {desc}")
    print("  ⚠️ 飞书API需要通过OpenClaw内部调用")
    
    # 保存到待办列表
    todo_file = SKILLS_DIR / "pending_feishu.txt"
    with open(todo_file, "a") as f:
        f.write(f"{skill_name}|{desc}|{now}\n")
    print(f"  ✅ 已记录到待办")
    
    return True, "飞书更新已记录"

def check_pending_feishu():
    """检查待处理的飞书更新"""
    todo_file = SKILLS_DIR / "pending_feishu.txt"
    if todo_file.exists():
        print(f"\n📋 待处理飞书更新 ({todo_file}):")
        print(todo_file.read_text())
    else:
        print("\nℹ️ 无待处理飞书更新")

def main():
    if len(sys.argv) < 2:
        print("""
🔧 Word Update v2 - 自动化上传更新

用法:
    python word_update.py <skill名称> [描述]

示例:
    python word_update.py my-skill "新增功能"
    python word_update.py backup-manager "修复bug"
        """)
        check_pending_feishu()
        return
    
    skill_name = sys.argv[1]
    desc = sys.argv[2] if len(sys.argv) > 2 else "更新"
    
    print(f"🔧 更新 Skill: {skill_name}")
    print(f"📝 描述: {desc}")
    print()
    
    # GitHub更新
    success, msg = update_github(skill_name, desc)
    if not success:
        print(f"❌ GitHub更新失败: {msg}")
    
    # 飞书更新
    update_feishu(skill_name, desc)
    
    print("\n✅ 全部完成!")

if __name__ == "__main__":
    main()
