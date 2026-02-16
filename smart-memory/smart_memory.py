#!/usr/bin/env python3
"""
智能记忆管理器 - Smart Memory v5

适配新对话格式：包含时间戳的简短指令
"""

import json
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

def parse_messages(session_file):
    """提取所有消息"""
    user_msgs = []
    assistant_msgs = []
    try:
        with open(session_file) as fp:
            for line in fp:
                try:
                    data = json.loads(line)
                    if data.get('type') == 'message':
                        msg = data.get('message', {})
                        role = msg.get('role', '')
                        content = msg.get('content', [])
                        if isinstance(content, list):
                            for c in content:
                                if c.get('type') == 'text':
                                    text = c.get('text', '')
                                    if text and len(text) > 3:
                                        if role == 'user':
                                            user_msgs.append(text)
                                        else:
                                            assistant_msgs.append(text[:200])
                except:
                    continue
    except:
        pass
    return user_msgs[-20:], assistant_msgs[-20:]

def extract_info(user_msgs, assistant_msgs) -> dict:
    """提取关键信息"""
    info = {"偏好": [], "规则": [], "重要": [], "待办": [], "技能": [], "项目": []}
    all_text = "\n".join(user_msgs + assistant_msgs)
    lines = all_text.split('\n')
    
    # 从用户消息中提取
    for line in user_msgs:
        line = line.strip()
        if len(line) < 10 or "Mon" in line or "GMT" in line:
            continue
        
        lower = line.lower()
        
        # 偏好
        if any(k in lower for k in ["我喜欢", "我想要", "我习惯", "我希望", "我不喜欢"]):
            info["偏好"].append(line[:80])
        
        # 规则
        elif any(k in lower for k in ["记住", "规则", "必须", "不要", "已设置", "已记录"]):
            info["规则"].append(line[:80])
        
        # 重要信息
        elif any(k in lower for k in ["重要", "关键", "核心", "必须记住"]):
            info["重要"].append(line[:80])
        
        # 待办
        elif any(k in lower for k in ["待办", "还要", "需要做", "完成"]):
            info["待办"].append(line[:80])
    
    # 从助手消息中提取项目/技能
    for line in assistant_msgs:
        line = line.strip()
        if len(line) < 15 or len(line) > 120:
            continue
        lower = line.lower()
        
        if any(k in lower for k in ["skill", "开发", "创建", "完成"]):
            info["技能"].append(line)
        
        if any(k in lower for k in ["项目", "正在", "构建"]):
            info["项目"].append(line[:80])
    
    # 去重
    for k in info:
        unique = []
        for item in info[k]:
            if item not in unique and len(item) > 5:
                unique.append(item)
        info[k] = unique[:6]
    
    return info

def generate_qmd(files, layer, days):
    all_user = []
    all_assistant = []
    for f in files[:8]:
        user_msgs, assistant_msgs = parse_messages(f)
        all_user.extend(user_msgs)
        all_assistant.extend(assistant_msgs)
    
    info = extract_info(all_user, all_assistant)
    
    qmd = f"""# 记忆分层 - {layer}

**层级**: {layer}
**时间范围**: 最近 {days} 天
**对话数**: {len(files)}
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

"""
    
    titles = {"偏好": "偏好", "规则": "规则", "重要": "重要信息", "待办": "待办", "技能": "创建的技能", "项目": "项目"}
    
    for cat, title in titles.items():
        if info.get(cat):
            qmd += f"## {title}\n\n"
            for item in info[cat][:5]:
                qmd += f"- {item}\n"
            qmd += "\n"
    
    return qmd

def analyze():
    print("\n📊 记忆状态分析")
    print("="*50)
    total = 0
    for layer, days in LAYERS.items():
        files = get_recent_files(days)
        size = sum(f.stat().st_size for f in files) / 1024
        print(f"{layer}: {len(files)}个, {size:.1f}KB")
        total += size
    print(f"\n总计: {total:.1f}KB")
    print("⚠️ 建议优化" if total > 500 else "✅ 良好")

def create():
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    print("\n🔧 创建分层记忆...")
    for layer, days in LAYERS.items():
        files = get_recent_files(days)
        if files:
            qmd = MEMORY_DIR / f"layer_{layer}.md"
            qmd.write_text(generate_qmd(files, layer, days))
            print(f"✅ {layer}")
    
    perm = MEMORY_DIR / "permanent.md"
    if not perm.exists():
        perm.write_text("# 永久记忆\n\n## 用户信息\n\n## 核心规则\n\n## 技能偏好\n")
        print(f"✅ permanent")
    print("\n🎉 完成!")

def read(layer=None):
    if layer:
        f = MEMORY_DIR / f"layer_{layer}.md"
        if f.exists():
            print(f"\n📖 {layer}:\n{f.read_text()}")
    else:
        for l in ["short_term", "long_term", "permanent"]:
            f = MEMORY_DIR / f"layer_{l}.md"
            if f.exists():
                print(f"\n{'='*40}\n📖 {l}\n{'='*40}\n{f.read_text()[:500]}")

def main():
    import sys
    if len(sys.argv) < 2:
        print("""
🔧 Smart Memory v5 - 智能记忆管理器
用法:
  smart_memory.py analyze  # 分析
  smart_memory.py create  # 创建
  smart_memory.py read    # 读取
        """)
        return
    {"analyze": analyze, "create": create, "read": read}.get(sys.argv[1], lambda: print("?"))()

if __name__ == "__main__":
    main()
