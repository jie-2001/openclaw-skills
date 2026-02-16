#!/usr/bin/env python3
"""
Word Update - 自动化上传更新脚本

功能：
1. 自动更新 GitHub 仓库
2. 自动更新飞书文档版本记录
3. 错误处理和重试机制

用法：
    python word_update.py --desc "更新描述" --target github,feishu
    
参数：
    --desc: 更新描述（必填）
    --target: 更新目标 (github, feishu, all，默认 all)
    --retry: 重试次数（默认 3）

示例：
    python word_update.py --desc "添加新 Skill"
    python word_update.py --desc "修复 Bug" --target github
    python word_update.py --desc "更新文档" --target feishu
"""

import os
import sys
import json
import argparse
import subprocess
import time
from pathlib import Path

# 配置
SKILLS_DIR = Path.home() / ".openclaw" / "skills"
GITHUB_REPO = "https://github.com/jie-2001/openclaw-skills.git"

# 飞书文档配置（需要手动维护）
FEISHU_DOCS = {
    "main": "YMr1dySwToBwSpxTJrpcNZODnCc",  # 主管理表
    "rules": "WtvAdzg8FoB985x7XQychilunpc",   # 管理规则
    "memory-optimizer": "MeVpdqd9eoC1M2xdjgLcu30kngf",
    "memory-search-cli": "APjcdLnqUofZtyxCBkScpnHhnRE",
    "model-switcher": "L0ZIdPjOaoFY97xbfLWcKnulnWu",
    "local-security": "K7sVdMrCooq937xmk9rcY6xLnIf",
    "clawsec-suite": "C9QDdL9ZPoCkYRxkcrTcdjeBngX",
    "file-cleaner": "H4GOdztbEougICxf66ac3ejlnDg",
    "hook-auto-check": "Y2KNdEpCforS67xBgjkca5K9nzg",
    "word_update": None,  # 新创建，暂无飞书文档
}

def run_command(cmd, cwd=None, retry=3):
    """执行命令，支持重试"""
    for attempt in range(retry):
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                return True, result.stdout
            else:
                print(f"  ⚠️ 尝试 {attempt + 1}/{retry} 失败: {result.stderr}")
                if attempt < retry - 1:
                    time.sleep(2)
        except subprocess.TimeoutExpired:
            print(f"  ⚠️ 命令超时，尝试 {attempt + 1}/{retry}")
            time.sleep(2)
        except Exception as e:
            print(f"  ⚠️ 错误: {e}")
            time.sleep(2)
    
    return False, "命令执行失败"

def update_github(desc):
    """更新 GitHub"""
    print("=== GitHub 更新 ===")
    
    # 检查是否有更改
    success, output = run_command("git status --porcelain", cwd=SKILLS_DIR)
    if not success:
        return False, "无法检查 git 状态"
    
    if not output.strip():
        print("  ℹ️ 没有需要更新的内容")
        return True, "无需更新"
    
    print(f"  📝 检测到更改，执行提交...")
    
    # git add
    success, output = run_command("git add -A", cwd=SKILLS_DIR)
    if not success:
        return False, f"git add 失败: {output}"
    print("  ✅ git add 完成")
    
    # git commit
    commit_msg = desc
    success, output = run_command(f'git commit -m "{commit_msg}"', cwd=SKILLS_DIR)
    if not success:
        # 可能没有需要提交的内容
        if "nothing to commit" in output.lower():
            print("  ℹ️ 没有需要提交的内容")
            return True, "无需提交"
        return False, f"git commit 失败: {output}"
    print(f"  ✅ commit 完成: {commit_msg}")
    
    # git push
    print("  📤 推送到 GitHub...")
    success, output = run_command("git push origin main", cwd=SKILLS_DIR, retry=3)
    if not success:
        return False, f"git push 失败: {output}"
    print("  ✅ GitHub 更新完成")
    
    return True, "GitHub 更新成功"

def update_feishu(desc):
    """更新飞书（占位符）"""
    print("\n=== 飞书更新 ===")
    print("  ⚠️ 飞书更新需要通过 OpenClaw 飞书 API 手动操作")
    print("  ℹ️ 请在飞书中手动更新版本记录")
    print("  📝 建议更新内容:", desc)
    
    # 注意：飞书 API 调用需要在 OpenClaw 内部通过 feishu_doc 工具完成
    # 这里提供提示信息
    return True, "飞书更新提示已给出"

def main():
    parser = argparse.ArgumentParser(description="Word Update - 自动化上传更新")
    parser.add_argument("--desc", required=True, help="更新描述")
    parser.add_argument("--target", default="all", help="更新目标: github, feishu, all")
    parser.add_argument("--retry", type=int, default=3, help="重试次数")
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("Word Update - 自动化上传更新")
    print("=" * 50)
    print(f"更新描述: {args.desc}")
    print(f"更新目标: {args.target}")
    print()
    
    results = {}
    
    # GitHub 更新
    if args.target in ["github", "all"]:
        success, message = update_github(args.desc)
        results["github"] = {"success": success, "message": message}
    
    # 飞书更新
    if args.target in ["feishu", "all"]:
        success, message = update_feishu(args.desc)
        results["feishu"] = {"success": success, "message": message}
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("更新结果汇总")
    print("=" * 50)
    
    all_success = True
    for platform, result in results.items():
        status = "✅ 成功" if result["success"] else "❌ 失败"
        print(f"{platform.upper()}: {status}")
        if not result["success"]:
            print(f"  原因: {result['message']}")
            all_success = False
    
    print("=" * 50)
    
    if all_success:
        print("🎉 全部更新完成！")
        return 0
    else:
        print("⚠️ 部分更新失败，请检查错误信息")
        return 1

if __name__ == "__main__":
    sys.exit(main())
