#!/usr/bin/env python3
"""
智能记忆管理器 - 适配实际格式

提取用户消息（带时间戳格式）
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta

WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_DIR = WORKSPACE / "memory"
AGENTS_DIR = Path.home() / ".openclaw" / "agents" / "main" / "sessions"

LAYERS = {"short_term": 7, "long_term": 30}

def get_recent_files(days=7):
    cutoff = datetime.now() - timedelta(days=days)
    files = []
    if not AGENTS_DIR.exists():
        return files
    for f in AGENTS_DIR.glob("*.jsonl"):
        if f.name.endswith('.lock'):
            continue
        try:
            if datetime.fromtimestamp(f.stat().st_mtime) > cutoff:
                files.append(f)
        except:
            continue
    return sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)

def extract_user_messages(files):
    """提取用户消息"""
    messages = []
    for f in files:
        try:
            with open(f) as fp:
                for line in fp:
                    try:
                        data = json.loads(line)
                        if data.get('type') == 'message':
                            msg = data.get('message', {})
                            if msg.get('role') == 'user':
                                content = msg.get('content', [])
                                if content and isinstance(content, list):
                                    for c in content:
                                        if c.get('type') == 'text':
                                            text = c.get('text', '')
                                            if text:
                                                messages.append(text)
                    except:
                        continue
        except:
            continue
    return messages[-30:]

def clean_message(msg):
    """清理消息"""
    # 去掉时间戳 [Tue 2026-02-17 03:15 GMT+8]
    msg = re.sub(r'\[.*?\]', '', msg).strip()
    # 去掉System:
    msg = re.sub(r'^System:.*', '', msg).strip()
    # 跳过太短或太长的
    if len(msg) < 10 or len(msg) > 150:
        return None
    return msg

def generate_qmd(files, layer, days):
    messages = extract_user_messages(files)
    cleaned = [clean_message(m) for m in messages]
    cleaned = [m for m in cleaned if m]
    
    qmd = f"""# 记忆 - {layer}

**层级**: {layer}
**时间范围**: 最近 {days} 天
**对话数**: {len(files)}
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 用户指令 ({len(cleaned)}条)

"""
    
    for i, msg in enumerate(cleaned[-10:], 1):
        qmd += f"{i}. {msg}\n"
    
    return qmd

def analyze():
    print("\n📊 记忆状态")
    print("="*40)
    total = 0
    for layer, days in LAYERS.items():
        files = get_recent_files(days)
        size = sum(f.stat().st_size for f in files) / 1024
        print(f"{layer}: {len(files)}个, {size:.0f}KB")
        total += size
    print(f"\n总计: {total:.0f}KB")
    print("⚠️ 建议优化" if total > 500 else "✅ 良好")

def create():
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    print("\n🔧 创建记忆...")
    for layer, days in LAYERS.items():
        files = get_recent_files(days)
        if files:
            qmd = MEMORY_DIR / f"layer_{layer}.md"
            qmd.write_text(generate_qmd(files, layer, days))
            print(f"✅ {layer}")
    
    perm = MEMORY_DIR / "permanent.md"
    if not perm.exists():
        perm.write_text("# 永久记忆\n\n## 用户\n\n## 规则\n\n## 技能\n")
    print("✅ 完成!")

def read(layer=None):
    for l in ["short_term", "long_term", "permanent"]:
        f = MEMORY_DIR / f"layer_{l}.md"
        if f.exists():
            print(f"\n=== {l} ===\n{f.read_text()[:400]}")

def main():
    import sys
    if len(sys.argv) < 2:
        print("用法: smart_memory.py [analyze|create|read]")
        return
    {"analyze": analyze, "create": create, "read": read}.get(sys.argv[1], lambda: print("?"))()

if __name__ == "__main__":
    main()
