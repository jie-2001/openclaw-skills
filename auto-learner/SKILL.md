# Auto-Learner - 自动学习器

## 概述

自动学习器是一个自主运行的skill，能够在指定时间内不间断地：
1. 自检现有skills状态
2. 从GitHub学习openclaw、n8n、dify等相关内容
3. 整理成学习报告
4. 自动继续执行，无需询问用户

## 文件结构

```
auto-learner/
├── SKILL.md           # 本文件
└── auto_learner.py    # 主程序
```

## 触发条件

当用户说以下内容时激活：
- "开始学习"
- "自动学习"
- "学习模式"
- "运行auto-learner"
- "学习github内容"

## 使用方法

### 基本用法
```bash
python3 ~/.openclaw/skills/auto-learner/auto_learner.py
# 默认学习1小时
```

### 指定学习时间
```bash
python3 ~/.openclaw/skills/auto-learner/auto_learner.py 2
# 学习2小时
```

## 功能

### 1. 自检现有Skills
- 扫描 ~/.openclaw/skills/ 目录
- 分析每个skill的结构
- 给出优化建议

### 2. GitHub学习
自动搜索以下主题：
- openclaw
- n8n  
- dify
- automation
- ai-agent

获取高星项目信息：
- 项目名称
- 描述
- Star数量
- 链接

### 3. 生成报告
自动生成Markdown格式学习报告，包含：
- 当前skills列表
- GitHub学习成果
- 优化建议

### 4. 自动继续
- 支持长时间运行
- 自动检查时间
- 完成后保存报告

## 输出

报告保存在：`~/.openclaw/workspace/learning/`

文件名格式：`report_YYYYMMDD_HHMMSS.md`

## 示例输出

```
[08:00:00] 🚀 开始自动学习 (目标: 1小时)
[08:00:01] 🔍 自检现有Skills...
[08:00:01]    现有 15 个Skills
[08:00:01]    💡 建议: 3个skill没有Python脚本
[08:00:02] 🔎 搜索 GitHub: openclaw
[08:00:02]    找到 5 个相关项目
...
[08:30:00] ✅ 学习完成!
```

## 注意事项

1. 首次运行会安装requests库（如需要）
2. GitHub API有速率限制，搜索间隔1秒
3. 报告自动保存到workspace目录
4. 可随时Ctrl+C中断

---

**版本**: 1.0.0  
**作者**: Auto-Learner  
**更新**: 2026-02-17
