# smart-memory 智能记忆管理器

## 功能
1. 分层记忆：短期(7天)/长期(30天)/永久
2. QMD格式输出
3. 自动提取关键信息（偏好、规则、事实）
4. 记忆状态分析

## 使用方法

```bash
# 分析记忆状态
python3 smart_memory.py analyze

# 创建分层记忆
python3 smart_memory.py create

# 读取所有记忆
python3 smart_memory.py read

# 读取特定层级
python3 smart_memory.py read short_term
python3 smart_memory.py read long_term
python3 smart_memory.py read permanent
```

## 输出位置
~/.openclaw/workspace/memory/
- layer_short_term.md
- layer_long_term.md
- permanent.md
