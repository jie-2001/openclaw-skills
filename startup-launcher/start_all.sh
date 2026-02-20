#!/bin/bash
# 启动所有常驻服务

SKILL_DIR="/home/lhj/.openclaw/skills/startup-launcher"
LOG_DIR="$SKILL_DIR/logs"

mkdir -p "$LOG_DIR"

echo "========================================="
echo "🚀 启动 OpenClaw 常驻服务"
echo "========================================="

# 1. 启动 Port Manager (10086)
echo ""
echo "📡 启动 Port Manager (10086)..."
if ss -tuln | grep -q ":10086 "; then
    echo "   ✅ Port Manager 已运行"
else
    cd ~/.openclaw/workspace/port_manager
    nohup python3 port_manager.py > "$LOG_DIR/port_manager.log" 2>&1 &
    echo "   ✅ Port Manager 已启动 (PID: $!)"
fi

# 2. 启动 OpenLLM Monitor (3000)
echo ""
echo "📊 启动 OpenLLM Monitor (3000)..."
if ss -tuln | grep -q ":3000 "; then
    echo "   ✅ OpenLLM Monitor 已运行"
else
    cd ~/.openclaw/workspace/OpenLLM-Monitor
    nohup docker-compose up -d > "$LOG_DIR/openllm_monitor.log" 2>&1 &
    echo "   ✅ OpenLLM Monitor 已启动"
fi

# 3. 启动 Port Monitor (后台任务，由 Cron 调度)
echo ""
echo "🔍 Port Monitor 由 Cron 调度..."

echo ""
echo "========================================="
echo "✅ 所有服务启动完成"
echo "========================================="
echo ""
echo "📋 服务地址："
echo "   - Port Manager: http://localhost:10086"
echo "   - OpenLLM Monitor: http://localhost:3000"
