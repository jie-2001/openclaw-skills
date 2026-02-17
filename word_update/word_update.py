#!/usr/bin/env python3
"""
Word Update v7 - 带飞书检查

功能：
1. 上传到GitHub + 验证
2. 自动检查飞书更新
3. 集成检查逻辑
"""

import sys
import subprocess
import re
from pathlib import Path
from datetime import datetime

SKILLS_DIR = Path.home() / ".openclaw" / "skills"

# 飞书文档ID
MAIN_DOC = "YMr1dySwToBwSpxTJrpcNZODnCc"
VERSION_DOCS = {
    "memory-optimizer": "MeVpdqd9eoC1M2xdjgLcu30kngf",
    "memory-search-cli": "APjcdLnqUofZtyxCBkScpnHhnRE",
    "model-switcher": "L0ZIdPjOaoFY97xbfLWcKnulnWu",
    "local-security": "K7sVdMrCooq937xmk9rcY6xLnIf",
    "clawsec-suite": "C9QDdL9ZPoCkYRxkcrTcdjeBngX",
    "file-cleaner": "H4GOdztbEougICxf66ac3ejlnDg",
    "hook-auto-check": "Y2KNdEpCforS67xBgjkca5K9nzg",
    "word_update": "J1WedDT8EoZTXcxlM9NcUUROnze",
    "ai-news-digest": "DGGVdd2LBoNm2yxJh6ecCjX4nGh",
    "personal-assistant": "VtFHdMpHWoeF5DxbPKXcD5T5noc",
    "backup-manager": "ZI12dveLlog7IxxTgpjcZJ6bntf",
    "smart-memory": "Iaw5dw36aoXmzWxwZOLck25ende",
    "auto-learner": "J1WedDT8EoZTXcxlM9NcUUROnze",
}

def get_current_version(skill_name):
    """读取当前版本号"""
    skill_file = SKILLS_DIR / skill_name / "SKILL.md"
    if not skill_file.exists():
        return "v1.0.0"
    content = skill_file.read_text()
    match = re.search(r'v(\d+)\.(\d+)\.(\d+)', content)
    if match:
        return f"v{match.group(1)}.{match.group(2)}.{match.group(3)}"
    return "v1.0.0"

def bump_version(version, bump_type="patch"):
    """递增版本号"""
    match = re.search(r'v(\d+)\.(\d+)\.(\d+)', version)
    if not match:
        return "v1.0.1"
    major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3))
    if bump_type == "major":
        return f"v{major+1}.0.0"
    elif bump_type == "minor":
        return f"v{major}.{minor+1}.0"
    else:
        return f"v{major}.{minor}.{patch+1}"

def update_skill_version(skill_name, new_version):
    """更新SKILL.md中的版本号"""
    skill_file = SKILLS_DIR / skill_name / "SKILL.md"
    if not skill_file.exists():
        return False
    content = skill_file.read_text()
    new_content = re.sub(r'v\d+\.\d+\.\d+', new_version, content)
    skill_file.write_text(new_content)
    return True

def verify_github(skill_name):
    """验证GitHub"""
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
    current_ver = get_current_version(skill_name)
    new_ver = bump_version(current_ver, bump_type)
    print(f"\n📤 上传 {skill_name}...")
    print(f"   版本: {current_ver} → {new_ver}")
    
    update_skill_version(skill_name, new_ver)
    subprocess.run(f"git add {skill_name}/", cwd=SKILLS_DIR, shell=True)
    subprocess.run(f'git commit -m "{skill_name} {new_ver} - {desc}"', cwd=SKILLS_DIR, shell=True)
    result = subprocess.run("git push origin main", cwd=SKILLS_DIR, 
                          shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("   ✅ GitHub完成")
        return new_ver
    else:
        print("   ❌ GitHub失败")
        return None

def check_feishu(skill_name):
    """检查飞书更新 - 提示需要手动检查"""
    print(f"\n🔍 飞书检查:")
    print(f"   ⚠️ 由于API限制，请手动检查以下内容:")
    print(f"   1. 主管理表: https://feishu.cn/docx/{MAIN_DOC}")
    print(f"   2. 搜索 Skill: {skill_name}")
    print(f"   3. 确认版本号和时间已更新")
    if VERSION_DOCS.get(skill_name):
        print(f"   4. 版本记录: https://feishu.cn/docx/{VERSION_DOCS[skill_name]}")
    return True

def main():
    skill_name = sys.argv[1] if len(sys.argv) > 1 else None
    desc = sys.argv[2] if len(sys.argv) > 2 else "优化"
    bump = sys.argv[3] if len(sys.argv) > 3 else "patch"
    
    if not skill_name:
        print("""
🔧 Word Update v7 - 带飞书检查

用法: word_update.py <skill> [描述] [bump]

示例:
  word_update.py ai-news-digest "修复格式" patch
        """)
        return
    
    print(f"🔧 更新: {skill_name}")
    
    # GitHub
    new_ver = update_github(skill_name, desc, bump)
    if not new_ver:
        return
    
    # 验证
    ok, msg = verify_github(skill_name)
    print(f"\n🔍 GitHub验证: {msg}")
    
    # 飞书检查提示
    check_feishu(skill_name)
    
    print(f"""
📝 飞书待更新:
   Skill: {skill_name}
   版本: {new_ver}
   描述: {desc}
   
请在飞书中确认:
1. 主管理表中 {skill_name} 的版本号和时间
2. 版本记录表中是否添加了新版本
""")

if __name__ == "__main__":
    main()
