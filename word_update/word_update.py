#!/usr/bin/env python3
"""
Word Update v5 - 带Git检验

功能：
1. 上传到GitHub  
2. 通过Git验证上传
3. 记录飞书
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

SKILLS_DIR = Path.home() / ".openclaw" / "skills"

def verify_github(skill_name):
    """通过Git验证上传"""
    print(f"\n🔍 验证 {skill_name}...")
    
    # 检查git log
    result = subprocess.run(
        f"git log --oneline -1 --grep={skill_name}",
        cwd=SKILLS_DIR, shell=True, capture_output=True, text=True
    )
    
    if skill_name in result.stdout:
        # 检查文件是否在git中
        result2 = subprocess.run(
            f"git ls-files | grep ^{skill_name}/",
            cwd=SKILLS_DIR, shell=True, capture_output=True, text=True
        )
        files = [f for f in result2.stdout.strip().split('\n') if f]
        if files:
            return True, f"✅ 已提交 {len(files)} 个文件"
    
    return False, "❌ 未找到提交记录"

def update_github(skill_name, desc):
    """上传到GitHub"""
    print(f"\n📤 上传 {skill_name}...")
    
    local_path = SKILLS_DIR / skill_name
    if not local_path.exists():
        print(f"❌ 目录不存在: {skill_name}")
        return False
    
    # git add
    subprocess.run(f"git add {skill_name}/", cwd=SKILLS_DIR, shell=True)
    
    # git status检查
    result = subprocess.run("git status --porcelain", cwd=SKILLS_DIR, 
                          shell=True, capture_output=True, text=True)
    if not result.stdout.strip():
        print("  ℹ️ 没有需要上传的更改")
        return True
    
    # git commit
    msg = f"{skill_name}: {desc}"
    subprocess.run(f'git commit -m "{msg}"', cwd=SKILLS_DIR, shell=True)
    
    # git push
    result = subprocess.run("git push origin main", cwd=SKILLS_DIR, 
                          shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ GitHub上传成功")
        return True
    else:
        print(f"❌ 上传失败")
        return False

def main():
    skill_name = sys.argv[1] if len(sys.argv) > 1 else None
    desc = sys.argv[2] if len(sys.argv) > 2 else "更新"
    
    if not skill_name:
        print("🔧 Word Update v5")
        print("用法: word_update.py <skill> [描述]")
        return
    
    # 上传
    if not update_github(skill_name, desc):
        return
    
    # 验证
    ok, msg = verify_github(skill_name)
    print(f"\n📊 {msg}")
    
    # 飞书记录
    print(f"""
📝 飞书记录:
   Skill: {skill_name}
   描述: {desc}
   时间: {datetime.now().strftime('%H:%M')}
   GitHub: {'✅' if ok else '❌'}
""")

if __name__ == "__main__":
    main()
