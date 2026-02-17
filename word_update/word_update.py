#!/usr/bin/env python3
"""
Word Update v4 - 带检验功能

功能：
1. 上传到GitHub
2. 检验上传是否成功
3. 记录飞书待办
"""

import sys
import subprocess
import json
import requests
from pathlib import Path
from datetime import datetime

SKILLS_DIR = Path.home() / ".openclaw" / "skills"
GITHUB_REPO = "jie-2001/openclaw-skills"
GITHUB_API = "https://api.github.com"

def get_github_files(path=""):
    """获取GitHub上的文件列表"""
    url = f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{path}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return []

def check_github_upload(skill_name):
    """检验GitHub上传"""
    print(f"\n🔍 检验 {skill_name} 上传状态...")
    
    local_path = SKILLS_DIR / skill_name
    if not local_path.exists():
        return False, "本地目录不存在"
    
    # 获取本地文件
    local_files = []
    for f in local_path.rglob("*"):
        if f.is_file() and not f.name.startswith('.'):
            local_files.append(f.relative_to(SKILLS_DIR))
    
    # 获取GitHub文件
    github_files = get_github_files(f"skills/{skill_name}")
    if isinstance(github_files, list):
        github_names = {f['name'] for f in github_files}
    else:
        github_names = set()
    
    # 比较
    local_names = {f.name for f in local_files}
    missing = local_names - github_names
    extra = github_names - local_names
    
    if not missing and not extra:
        return True, f"✅ 全部 {len(local_names)} 个文件已上传"
    else:
        msg = []
        if missing:
            msg.append(f"缺失: {', '.join(missing)}")
        if extra:
            msg.append(f"多余: {', '.join(extra)}")
        return False, "; ".join(msg)

def update_github(skill_name, desc):
    """上传到GitHub"""
    print(f"\n📤 上传 {skill_name}...")
    
    # git add
    subprocess.run(f"git add {skill_name}/", cwd=SKILLS_DIR, shell=True)
    
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
        print(f"❌ GitHub上传失败: {result.stderr}")
        return False

def main():
    skill_name = sys.argv[1] if len(sys.argv) > 1 else None
    desc = sys.argv[2] if len(sys.argv) > 2 else "更新"
    
    if not skill_name:
        # 检验模式
        print("🔍 Word Update v4 - 检验模式")
        print("用法: word_update.py <skill名称> [描述]")
        
        # 列出所有skills
        print("\n📋 本地Skills:")
        for d in sorted(SKILLS_DIR.iterdir()):
            if d.is_dir() and not d.name.startswith('.') and not d.is_symlink():
                if (d / "SKILL.md").exists():
                    print(f"  - {d.name}")
        return
    
    # 1. 上传
    success = update_github(skill_name, desc)
    if not success:
        print("\n❌ 上传失败，终止")
        return
    
    # 2. 检验
    # 等待GitHub同步
    print("⏳ 等待GitHub同步(3秒)...")
    import time
    time.sleep(3)
    
    ok, msg = check_github_upload(skill_name)
    print(f"\n📊 检验结果: {msg}")
    
    if ok:
        # 3. 记录飞书
        print("\n📝 飞书记录:")
        print(f"   Skill: {skill_name}")
        print(f"   描述: {desc}")
        print(f"   时间: {datetime.now().strftime('%H:%M')}")
        print("   状态: ✅ GitHub已验证")
    else:
        print(f"\n⚠️ 警告: {msg}")

if __name__ == "__main__":
    main()
