# backup-manager 底层逻辑备份管理器

## 功能
1. 备份当前底层逻辑到指定目录
2. 列出所有备份
3. 恢复指定备份
4. 比较当前与备份的差异

## 使用方法

```bash
# 创建备份
python3 backup_manager.py backup

# 列出备份
python3 backup_manager.py list

# 恢复备份
python3 backup_manager.py restore --name <备份名称>

# 比较差异
python3 backup_manager.py diff --name <备份名称>
```

## 备份内容
- MEMORY.md
- AGENTS.md
- SOUL.md
- USER.md
- TOOLS.md
- IDENTITY.md

## 备份位置
~/.openclaw/backup/
