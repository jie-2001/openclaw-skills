#!/usr/bin/env python3
"""
Word Update v6 - 完整版（版本号管理+飞书更新）

功能：
1. 自动版本号管理
2. 上传GitHub + 验证
3. 更新飞书版本记录
"""

import sys
import subprocess
import re
from pathlib import Path
from datetime import datetime

SKILLS_DIR = Path.home() / ".openclaw" / "skills"

# 飞书文档映射
FEISHU_DOCS = {
    "auto-learner": "J1WedDT8EoZTXcxlM9NcUUROnze",
    # 更多映射...
}

def get_current_version(skill_name):
    """读取当前版本号"""
    skill_file = SKILLS_DIR / skill_name / "SKILL.md"
    if not skill_file.exists():
        return "v1.0.0"
    
    content = skill_file.read_text()
    # 查找版本号 v1.0.0 格式
    match = re.search(r'v(\d+)\.(\d+)\.(\d+)', content)
    if match:
        return f"v{match.group(1)}.{match.group(2)}.{match.group(3)}"
    return "v1.0.0"

def bump_version(version, bump_type="patch"):
    """自动递增版本号"""
    match = re.search(r'v(\d+)\.(\d+)\.(\d+)', version)
    if not match:
        return "v1.0.1"
    
    major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3))
    
    if bump_type == "major":
        return f"v{major+1}.0.0"
    elif bump_type == "minor":
        return f"v{major}.{minor+1}.0"
    else:  # patch
        return f"v{major}.{minor}.{patch+1}"

def update_skill_version(skill_name, new_version):
    """更新SKILL.md中的版本号"""
    skill_file = SKILLS_DIR / skill_name / "SKILL.md"
    if not skill_file.exists():
        return False
    
    content = skill_file.read_text()
    # 替换版本号
    new_content = re.sub(r'v\d+\.\d+\.\d+', new_version, content)
    skill_file.write_text(new_content)
    return True

def verify_github(skill_name):
    """验证GitHub上传"""
    result = subprocess.run(
        f"git log --oneline -1 --grep={skill_name}",
        cwd=SKILLS_DIR, shell=True, capture_output=True, text=True
    )
    if skill_name in result.stdout:
        result2 = subprocess.run(
            f"git ls-files | grep ^{skill_name}/",
            cwd=SKILLS_DIR, shell=True, capture_output=True, text=True
        )
        files = [f for f in result2.stdout.strip().split('\n') if f]
        if files:
            return True, f"✅ {len(files)}个文件"
    return False, "❌ 未找到"

def update_github(skill_name, desc, bump_type="patch"):
    """上传GitHub"""
    print(f"\n📤 上传 {skill_name}...")
    
    # 获取当前版本
    current_ver = get_current_version(skill_name)
    new_ver = bump_version(current_ver, bump_type)
    print(f"   版本: {current_ver} → {new_ver}")
    
    # 更新版本号
    update_skill_version(skill_name, new_ver)
    
    # git add
    subprocess.run(f"git add {skill_name}/", cwd=SKILLS_DIR, shell=True)
    
    # git commit
    msg = f"{skill_name} {new_ver} - {desc}"
    subprocess.run(f'git commit -m "{msg}"', cwd=SKILLS_DIR, shell=True)
    
    # git push
    result = subprocess.run("git push origin main", cwd=SKILLS_DIR, 
                          shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("   ✅ GitHub完成")
        return new_ver
    else:
        print("   ❌ GitHub失败")
        return None

def main():
    skill_name = sys.argv[1] if len(sys.argv) > 1 else None
    desc = sys.argv[2] if len(sys.argv) > 2 else "优化"
    bump = sys.argv[3] if len(sys.argv) > 3 else "patch"  # patch/minor/major
    
    if not skill_name:
        print("""
🔧 Word Update v6 - 版本管理

用法: word_update.py <skill> [描述] [bump类型]

bump类型:
  patch (默认) - 补丁版本 v1.0.0 → v1.0.1
  minor        - 次版本 v1.0.0 → v1.1.0  
  major       - 主版本 v1.0.0 → v2.0.0

示例:
  word_update.py auto-learner "新增功能"
  word_update.py word_update "重大更新" major
        """)
        return
    
    print(f"🔧 更新: {skill_name}")
    print(f"📝 描述: {desc}")
    print(f"📈 版本: {bump}")
    
    # 上传GitHub
    new_ver = update_github(skill_name, desc, bump)
    if not new_ver:
        return
    
    # 验证
    ok, msg = verify_github(skill_name)
    print(f"\n🔍 验证: {msg}")
    
    # 输出飞书更新说明
    print(f"""
📝 飞书更新:
   Skill: {skill_name}
   新版本: {new_ver}
   描述: {desc}
   
   需手动更新:
   1. 主管理表 - 添加更新记录
   2. 版本记录 - 添加 {new_ver} 记录
""")

if __name__ == "__main__":
    main()
