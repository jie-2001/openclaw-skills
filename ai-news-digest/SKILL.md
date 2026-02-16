# AI 重点摘要 Skill

## 功能说明
定时抓取 AI 相关资讯，通过 LLM 生成中文摘要，推送到飞书。

## 定时任务
- **每日 6:00** 自动推送（使用 LLM 生成中文摘要）

## 数据源
1. OpenAI Blog (RSS)
2. MIT Tech Review (RSS)
3. Google AI (RSS)

## 推送格式
```
🤖 今日 AI 要闻

📌 中文标题
   详细描述（2-4行）
   🔗 原文链接

（重复5条）
```

## 手动运行
```bash
# 获取原始数据
python3 ~/.openclaw/skills/ai-news-digest/ai_news_digest.py raw

# 直接运行
python3 ~/.openclaw/skills/ai-news-digest/ai_news_digest.py
```

## 文件位置
```
~/.openclaw/skills/ai-news-digest/
├── SKILL.md
└── ai_news_digest.py
```
