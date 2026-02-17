#!/usr/bin/env python3
"""
飞书更新检查工具 - 使用OpenClaw的feishu_doc工具

用法:
    python feishu_check.py <skill名称>
    
说明:
    此脚本通过调用 OpenClaw 会话来检查飞书更新
    需要在 OpenClaw 环境中运行
"""

import sys
import subprocess
import json
import re
from pathlib import Path
from datetime import datetime

# Skill版本记录表映射
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

MAIN_DOC = "YMr1dySwToBwSpxTJrpcNZODnCc"

def check_via_openclaw(skill_name):
    """通过OpenClaw检查飞书"""
    print(f"\n🔍 检查飞书更新: {skill_name}")
    print("=" * 50)
    
    # 使用curl调用飞书API获取主文档
    cmd = '''curl -s "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
        -H "Content-Type: application/json" \
        -d '{"app_id":"cli_a91ad381ac385cc8","app_secret":"oLKH3P9yeQ5zIByQmdYnZg4GZ18wqewh"}' '''
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    try:
        token_data = json.loads(result.stdout)
        token = token_data.get("tenant_access_token", "")
    except:
        print("❌ 无法获取token")
        return False
    
    if not token:
        print("❌ Token获取失败")
        return False
    
    print(f"✅ Token获取成功")
    
    # 获取主文档内容
    cmd = f'''curl -s "https://open.feishu.cn/open-apis/doc/v1/documents/{MAIN_DOC}" \
        -H "Authorization: Bearer {token}" '''
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    # 尝试解析
    try:
        data = json.loads(result.stdout)
        content = data.get("data", {}).get("content", "")
    except:
        print("⚠️ API返回异常，尝试其他方式")
        content = ""
    
    # 简单检查
    checks = {
        "skill_exists": False,
        "version_found": None,
        "time_found": None,
    }
    
    # 查找skill块
    pattern = rf"## {skill_name}(.*?)(?=##|$)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        block = match.group(1)
        checks["skill_exists"] = True
        
        # 提取版本号
        ver_match = re.search(r"版本号:\s*(v\d+\.\d+\.\d+)", block)
        if ver_match:
            checks["version_found"] = ver_match.group(1)
        
        # 提取时间
        time_match = re.search(r"上传时间:\s*(\d{4}-\d{2}-\d{2}\s*\d{2}:\d{2})", block)
        if time_match:
            checks["time_found"] = time_match.group(1)
    
    # 输出结果
    print(f"\n📋 主管理表检查:")
    if checks["skill_exists"]:
        print(f"  ✅ Skill存在")
    else:
        print(f"  ❌ Skill不存在")
    
    if checks["version_found"]:
        print(f"  📌 版本号: {checks['version_found']}")
    else:
        print(f"  ⚠️ 未找到版本号")
    
    if checks["time_found"]:
        print(f"  🕐 上传时间: {checks['time_found']}")
    else:
        print(f"  ⚠️ 未找到上传时间")
    
    # 检查版本记录表
    doc_token = VERSION_DOCS.get(skill_name)
    print(f"\n📋 版本记录表检查:")
    if doc_token:
        print(f"  ✅ 映射存在: {doc_token[:20]}...")
    else:
        print(f"  ⚠️ 未找到版本记录表映射")
    
    return checks["skill_exists"]

def main():
    if len(sys.argv) < 2:
        print("""
🔧 飞书更新检查工具

用法:
    python feishu_check.py <skill名称>

示例:
    python feishu_check.py word_update
    python feishu_check.py ai-news-digest
        """)
        return
    
    skill_name = sys.argv[1]
    check_via_openclaw(skill_name)

if __name__ == "__main__":
    main()
