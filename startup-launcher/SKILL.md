# Startup Launcher Skill

_OpenClaw 开机启动器 - 自动启动所有常驻服务_

## 功能概述

- **统一管理**：所有需要在 OpenClaw 启动时自动运行的服务
- **服务列表**：
  - Port Manager (10086) - 端口管理界面
  - OpenLLM Monitor (3000) - API 监控仪表盘
  - Port Monitor - 端口监控告警

## 快速开始

### 查看服务状态

```bash
# 检查所有服务状态
~/.openclaw/skills/startup-launcher/check_services.sh
```

### 手动启动所有服务

```bash
~/.openclaw/skills/startup-launcher/start_all.sh
```

### 手动停止所有服务

```bash
~/.openclaw/skills/startup-launcher/stop_all.sh
```

## 服务说明

| 服务 | 端口 | 说明 |
|------|------|------|
| Port Manager | 10086 | 端口管理 Web 界面 |
| OpenLLM Monitor | 3000 | LLM API 监控仪表盘 |
| Port Monitor | (后台) | 端口监控 + 飞书告警 |

## 开机自启配置

通过 Cron 任务实现，详见下方。

## 访问地址

- Port Manager: http://localhost:10086
- OpenLLM Monitor: http://localhost:3000
