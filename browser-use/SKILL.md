# browser-use Skill

## 概述
AI浏览器自动化工具 - browser-use (78k⭐)

让AI代理能够控制浏览器自动执行任务。

## 项目信息
- **Stars**: 78k+
- **GitHub**: https://github.com/browser-use/browser-use

## 功能
- AI代理控制浏览器
- 自动执行网页任务
- 表单填写
- 数据抓取

## 安装
```bash
pip install browser-use
```

## 使用示例
```python
from browser_use import Agent
from langchain_openai import ChatOpenAI

agent = Agent(
    task="在知乎上搜索AI新闻",
    llm=ChatOpenAI(model="gpt-4")
)
agent.run()
```

## 集成说明
此Skill用于记录和学习browser-use项目，可与OpenClaw浏览器控制结合使用。

---

**版本**: v1.0.0  
**更新**: 2026-02-17
