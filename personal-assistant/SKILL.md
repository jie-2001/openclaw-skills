# personal-assistant 个人助手 Skill

## 功能说明
个人生活和工作管理助手，包含日程、任务、购物清单功能。

## 功能列表

### 1. 日程管理
- 添加日程
- 查看日程列表
- 删除日程

### 2. 工作进度（看板）
- 待办事项
- 进行中
- 已完成
- 任务状态移动

### 3. 购物清单
- 添加购物项
- 查看清单
- 标记完成

## 使用方法

```bash
# 日程
python3 personal_assistant.py schedule add <内容>
python3 personal_assistant.py schedule list

# 任务
python3 personal_assistant.py task add <内容>
python3 personal_assistant.py task list
python3 personal_assistant.py task move <编号> <todo|doing|done>

# 购物
python3 personal_assistant.py shopping add <内容>
python3 personal_assistant.py shopping list
python3 personal_assistant.py shopping done <编号>
```

## 数据存储
- 位置：`~/.openclaw/workspace/personal_assistant/`
- 格式：JSON 文件
