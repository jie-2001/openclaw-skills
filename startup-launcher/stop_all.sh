#!/bin/bash
# 停止所有常驻服务

SKILL_DIR="/home/lhj/.openclaw/skills/startup-launcher"

echo "========================================="
echo "🛑 停止 OpenClaw 常驻服务"
echo "========================================="

# 1. 停止 Port Manager
echo ""
echo "🛑 停止 Port Manager..."
pkill -f "port_manager.py" && echo "   ✅ 已停止" || echo "   ℹ️ 未运行"

# 2. 停止 OpenLLM Monitor
echo ""
echo "🛑 停止 OpenLLM Monitor..."
cd ~/.openclaw/workspace/OpenLLM-Monitor
docker-compose down > /dev/null 2>&1 && echo "   ✅ 已停止" || echo "   ℹ️ 未运行"

echo ""
echo "========================================="
echo "✅ 所有服务已停止"
echo "========================================="
