#!/usr/bin/env python3
"""
底层逻辑备份管理器

功能：
1. 备份当前底层逻辑到指定目录
2. 列出所有备份
3. 恢复指定备份
4. 比较当前与备份的差异

用途：
- 修改底层逻辑前先备份
- 出问题时快速恢复
"""

import os
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# 配置
BACKUP_DIR = Path("~/.openclaw/backup").expanduser()
SKILLS_DIR = Path("~/.openclaw/skills")

# 需要备份的核心文件
CORE_FILES = [
    "MEMORY.md",
    "AGENTS.md", 
    "SOUL.md",
    "USER.md",
    "TOOLS.md",
    "IDENTITY.md",
]

def create_backup(name=None):
    """创建备份"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    if not name:
        name = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    backup_path = BACKUP_DIR / name
    backup_path.mkdir(parents=True, exist_ok=True)
    
    # 复制核心文件
    copied = []
    for f in CORE_FILES:
        src = Path(f"~/.openclaw/workspace/{f}").expanduser()
        if src.exists():
            dst = backup_path / f
            shutil.copy2(src, dst)
            copied.append(f)
    
    # 保存备份元信息
    meta = {
        "name": name,
        "created": datetime.now().isoformat(),
        "files": copied
    }
    (backup_path / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    
    print(f"✅ 备份创建成功: {name}")
    print(f"   文件: {', '.join(copied)}")
    return name

def list_backups():
    """列出所有备份"""
    if not BACKUP_DIR.exists():
        print("暂无备份")
        return
    
    print("\n📦 可用备份：")
    print("-" * 40)
    
    backups = sorted(BACKUP_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)
    
    for b in backups:
        if b.is_dir():
            meta_file = b / "meta.json"
            if meta_file.exists():
                meta = json.loads(meta_file.read_text())
                print(f"  {b.name}")
                print(f"    时间: {meta['created'][:19]}")
                print(f"    文件: {', '.join(meta['files'])}")
                print()
            else:
                print(f"  {b.name} (无元信息)")

def restore_backup(name):
    """恢复备份"""
    backup_path = BACKUP_DIR / name
    
    if not backup_path.exists():
        print(f"❌ 备份不存在: {name}")
        return False
    
    # 复制文件回去
    restored = []
    for f in CORE_FILES:
        src = backup_path / f
        if src.exists():
            dst = Path(f"~/.openclaw/workspace/{f}").expanduser()
            shutil.copy2(src, dst)
            restored.append(f)
    
    print(f"✅ 恢复成功: {name}")
    print(f"   恢复文件: {', '.join(restored)}")
    return True

def diff_backup(name):
    """比较当前与备份的差异"""
    backup_path = BACKUP_DIR / name
    
    if not backup_path.exists():
        print(f"❌ 备份不存在: {name}")
        return
    
    print(f"\n🔍 比较当前与备份 '{name}' 的差异：")
    print("-" * 40)
    
    for f in CORE_FILES:
        src = Path(f"~/.openclaw/workspace/{f}").expanduser()
        dst = backup_path / f
        
        if not src.exists() and not dst.exists():
            continue
        
        if not src.exists():
            print(f"  + {f} (备份有，当前无)")
        elif not dst.exists():
            print(f"  - {f} (当前有，备份无)")
        else:
            src_content = src.read_text()
            dst_content = dst.read_text()
            if src_content != dst_content:
                print(f"  ~ {f} (有差异)")
            else:
                print(f"  = {f} (相同)")

def main():
    parser = argparse.ArgumentParser(description="底层逻辑备份管理器")
    parser.add_argument("action", choices=["backup", "restore", "list", "diff"], help="操作")
    parser.add_argument("--name", "-n", help="备份名称")
    
    args = parser.parse_args()
    
    if args.action == "backup":
        create_backup(args.name)
    elif args.action == "list":
        list_backups()
    elif args.action == "restore":
        if not args.name:
            print("请指定备份名称: --name <名称>")
        else:
            restore_backup(args.name)
    elif args.action == "diff":
        if not args.name:
            print("请指定备份名称: --name <名称>")
        else:
            diff_backup(args.name)

if __name__ == "__main__":
    main()
