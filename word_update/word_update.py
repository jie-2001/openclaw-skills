#!/usr/bin/env python3
"""Word Update v3 - 简化版"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

SKILLS_DIR = Path.home() / ".openclaw" / "skills"

def main():
    skill_name = sys.argv[1] if len(sys.argv) > 1 else None
    desc = sys.argv[2] if len(sys.argv) > 2 else "更新"
    
    if not skill_name:
        print("用法: word_update.py <skill名称> [描述]")
        return
    
    print(f"🔧 更新: {skill_name}")
    
    # GitHub
    print("📤 GitHub...")
    subprocess.run("git add -A", cwd=SKILLS_DIR, shell=True)
    subprocess.run(f'git commit -m "{skill_name}: {desc}"', cwd=SKILLS_DIR, shell=True)
    subprocess.run("git push origin main", cwd=SKILLS_DIR, shell=True)
    print("✅ GitHub完成")
    
    # 记录待处理
    print("📝 记录飞书待处理...")
    print("⚠️ 请手动运行以下飞书更新")
    print(f"   Skill: {skill_name}")
    print(f"   描述: {desc}")
    
if __name__ == "__main__":
    main()
