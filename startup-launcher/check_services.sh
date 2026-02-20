#!/bin/bash
# 检查所有服务状态

echo "========================================="
echo "📊 OpenClaw 常驻服务状态"
echo "========================================="
echo ""

# Port Manager
echo -n "📡 Port Manager (10086): "
if ss -tuln | grep -q ":10086 "; then
    echo "✅ 运行中"
else
    echo "❌ 未运行"
fi

# OpenLLM Monitor
echo -n "📊 OpenLLM Monitor (3000): "
if ss -tuln | grep -q ":3000 "; then
    echo "✅ 运行中"
else
    echo "❌ 未运行"
fi

# Port Monitor 进程
echo -n "🔍 Port Monitor (Cron): "
if pgrep -f "port_checker.py" > /dev/null; then
    echo "✅ 运行中"
else
    echo "ℹ️ 由 Cron 调度"
fi

echo ""
echo "📋 访问地址："
echo "   - Port Manager: http://localhost:10086"
echo "   - OpenLLM Monitor: http://localhost:3000"
