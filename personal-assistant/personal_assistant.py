#!/usr/bin/env python3
"""
个人助手 Skill

功能：
1. 日程提醒 - 添加、查看、删除日程
2. 工作进度 - 看板式任务管理
3. 购物清单 - 添加、完成、删除购物项

数据存储：~/.openclaw/workspace/personal_assistant/
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta

# 配置
DATA_DIR = Path("~/.openclaw/workspace/personal_assistant").expanduser()
DATA_DIR.mkdir(parents=True, exist_ok=True)

SCHEDULE_FILE = DATA_DIR / "schedule.json"
TASKS_FILE = DATA_DIR / "tasks.json"
SHOPPING_FILE = DATA_DIR / "shopping.json"

# 初始化文件
for f, default in [(SCHEDULE_FILE, []), (TASKS_FILE, {"todo": [], "doing": [], "done": []}), (SHOPPING_FILE, [])]:
    if not f.exists():
        f.write_text(json.dumps(default, ensure_ascii=False, indent=2))

def load_json(f):
    return json.loads(f.read_text())

def save_json(f, data):
    f.write_text(json.dumps(data, ensure_ascii=False, indent=2))

# ========== 日程管理 ==========
def add_schedule(content, time_str=None):
    """添加日程"""
    data = load_json(SCHEDULE_FILE)
    item = {
        "content": content,
        "time": time_str or datetime.now().strftime("%Y-%m-%d %H:%M"),
        "created": datetime.now().isoformat()
    }
    data.append(item)
    save_json(SCHEDULE_FILE, data)
    return f"✅ 已添加日程: {content}"

def list_schedule():
    """查看日程"""
    data = load_json(SCHEDULE_FILE)
    if not data:
        return "📭 暂无日程"
    
    msg = "📅 **今日日程**\n\n"
    for i, item in enumerate(data, 1):
        msg += f"{i}. {item['content']} ({item['time']})\n"
    return msg

# ========== 任务管理 ==========
def add_task(content, status="todo"):
    """添加任务"""
    data = load_json(TASKS_FILE)
    item = {
        "content": content,
        "status": status,
        "created": datetime.now().isoformat()
    }
    data[status].append(item)
    save_json(TASKS_FILE, data)
    return f"✅ 已添加任务: {content} (状态: {status})"

def list_tasks():
    """查看任务"""
    data = load_json(TASKS_FILE)
    msg = "📋 **工作进度**\n\n"
    
    for status, items in [("待办", data.get("todo", [])), ("进行中", data.get("doing", [])), ("已完成", data.get("done", []))]:
        msg += f"**{status}**\n"
        for i, item in enumerate(items, 1):
            msg += f"  {i}. {item['content']}\n"
        msg += "\n"
    return msg

def move_task(task_num, new_status):
    """移动任务状态"""
    data = load_json(TASKS_FILE)
    # 遍历所有列找任务
    for status in ["todo", "doing", "done"]:
        if 0 < task_num <= len(data.get(status, [])):
            task = data[status].pop(task_num - 1)
            task["status"] = new_status
            data[new_status].append(task)
            save_json(TASKS_FILE, data)
            return f"✅ 已将任务移动到: {new_status}"
    return "❌ 任务编号不存在"

# ========== 购物清单 ==========
def add_shopping(item):
    """添加购物项"""
    data = load_json(SHOPPING_FILE)
    data.append({"item": item, "done": False, "created": datetime.now().isoformat()})
    save_json(SHOPPING_FILE, data)
    return f"✅ 已添加购物项: {item}"

def list_shopping():
    """查看购物清单"""
    data = load_json(SHOPPING_FILE)
    if not data:
        return "📭 购物清单为空"
    
    msg = "🛒 **购物清单**\n\n"
    for i, item in enumerate(data, 1):
        status = "✅" if item.get("done") else "⬜"
        msg += f"{i}. {status} {item['item']}\n"
    return msg

def done_shopping(item_num):
    """标记完成"""
    data = load_json(SHOPPING_FILE)
    if 0 < item_num <= len(data):
        data[item_num - 1]["done"] = True
        save_json(SHOPPING_FILE, data)
        return f"✅ 已标记为完成: {data[item_num - 1]['item']}"
    return "❌ 编号不存在"

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
🤖 个人助手

用法:
  python3 personal_assistant.py schedule add <内容>     # 添加日程
  python3 personal_assistant.py schedule list           # 查看日程
  
  python3 personal_assistant.py task add <内容>         # 添加任务
  python3 personal_assistant.py task list              # 查看任务
  python3 personal_assistant.py task move <编号> <状态> # 移动任务 (todo/doing/done)
  
  python3 personal_assistant.py shopping add <内容>     # 添加购物
  python3 personal_assistant.py shopping list            # 查看购物
  python3 personal_assistant.py shopping done <编号>     # 标记完成
        """)
        return
    
    cmd = sys.argv[1]
    
    if cmd == "schedule":
        subcmd = sys.argv[2] if len(sys.argv) > 2 else None
        if subcmd == "add":
            print(add_schedule(" ".join(sys.argv[3:])))
        elif subcmd == "list":
            print(list_schedule())
    
    elif cmd == "task":
        subcmd = sys.argv[2] if len(sys.argv) > 2 else None
        if subcmd == "add":
            print(add_task(" ".join(sys.argv[3:])))
        elif subcmd == "list":
            print(list_tasks())
        elif subcmd == "move":
            print(move_task(int(sys.argv[3]), sys.argv[4]))
    
    elif cmd == "shopping":
        subcmd = sys.argv[2] if len(sys.argv) > 2 else None
        if subcmd == "add":
            print(add_shopping(" ".join(sys.argv[3:])))
        elif subcmd == "list":
            print(list_shopping())
        elif subcmd == "done":
            print(done_shopping(int(sys.argv[3])))

if __name__ == "__main__":
    main()
