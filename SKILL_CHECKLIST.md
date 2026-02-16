# Skill 开发完成检查清单

每次完成一个 Skill 后，必须执行以下所有步骤：

## ✅ 必做项（缺一不可）

### 1. 飞书管理表
- [ ] 更新「OpenClaw Skill 管理表」
- [ ] 添加 Skill 名称、版本号、描述

### 2. 飞书版本记录
- [ ] 创建版本记录文档（新建 Skill）
- [ ] 或更新现有文档（修改 Skill）

### 3. GitHub 同步
- [ ] git add
- [ ] git commit
- [ ] git push

---

## 📋 更新检查命令

```bash
# 检查是否有未提交的 Skill
cd ~/.openclaw/skills && git status

# 检查 Cron 任务
openclaw cron list
```

---

## ⚠️ 重要提醒

每次完成 Skill 开发后，**必须**立即执行上述所有步骤，不要等到最后一起处理！

本文件位置：`~/.openclaw/workspace/SKILL_CHECKLIST.md`
