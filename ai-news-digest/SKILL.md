# AI 重点摘要 Skill (增强版)

## 功能说明
定时抓取 AI 相关资讯、论文、技术趋势，通过 LLM 生成中文摘要，推送到飞书。

## 定时任务
- **每日 6:00** 自动推送（使用 LLM 生成中文摘要）

## 数据源

### 1. AI 新闻（原有）
- OpenAI Blog (RSS)
- MIT Tech Review (RSS)
- Google AI (RSS)

### 2. 论文检索（新增）
- **OpenAlex**: 学术论文数据库，支持 AI、机器学习等领域
- **arXiv**: 预印本平台，支持 cs.LG, cs.CV, cs.CL 等分类

### 3. GitHub Trending（新增）
- 抓取 GitHub 今日趋势仓库
- 按 stars 排序展示

### 4. 行业新闻（新增）
- TechCrunch
- Hacker News
- VentureBeat

## 推送格式
```
🤖 今日 AI 要闻 + 论文 + 技术趋势

=== 热门论文 ===
📄 [论文标题]
   ⭐⭐⭐⭐ | 分类 | 📊 X citations
   摘要片段...
   🔗 论文链接

=== GitHub 趋势 ===
🔥 [仓库名] ⭐ X stars
   描述...
   🔗 链接

=== AI 新闻 ===
📌 [中文标题]
   详细描述（2-4行）
   🔗 原文链接

（重复5条）
```

## 新增功能

### 相关性评分
对每篇论文进行 1-5 分评分：
- 5 = 核心AI/ML研究，高度相关
- 4 = 强相关
- 3 = 中等相关
- 2 = 弱相关
- 1 = 不相关

只推送评分 >= 3 的论文

### 去重机制
- 检查历史记录，避免重复推送
- 按 DOI 或 ID 去重

### 历史记录
- 保存已推送的论文/新闻到历史文件
- 支持查询历史记录

## 配置

```json
{
  "domain": {
    "name": "AI Research",
    "keywords": ["machine learning", "deep learning", "LLM", "GPT", "transformer"],
    "categories": ["NLP", "Computer Vision", "Reinforcement Learning", "Generative AI"]
  },
  "filters": {
    "minRelevanceScore": 3,
    "maxPapersPerDigest": 3,
    "maxNewsPerDigest": 5,
    "maxReposPerDigest": 5
  },
  "output": {
    "enabled": true,
    "feishu": true
  }
}
```

## 手动运行
```bash
# 获取原始数据
python3 ~/.openclaw/skills/ai-news-digest/ai_news_digest.py raw

# 直接运行
python3 ~/.openclaw/skills/ai-news-digest/ai_news_digest.py

# 只获取论文
python3 ~/.openclaw/skills/ai-news-digest/ai_news_digest.py papers

# 只获取 GitHub 趋势
python3 ~/.openclaw/skills/ai-news-digest/ai_news_digest.py repos
```

## 文件位置
```
~/.openclaw/skills/ai-news-digest/
├── SKILL.md
├── ai_news_digest.py
├── config.json
├── data/
│   ├── papers_history.jsonl
│   ├── repos_history.jsonl
│   └── news_history.jsonl
└── scripts/
    ├── fetch_papers.py
    ├── fetch_github.py
    └── fetch_news.py
```

## 依赖
- Python 3.8+
- requests
- feedparser
- beautifulsoup4
