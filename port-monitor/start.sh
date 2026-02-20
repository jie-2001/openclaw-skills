#!/bin/bash
# Port Monitor 启动脚本
# 用于 OpenClaw 开机自启动

SCRIPT_DIR="/home/lhj/.openclaw/skills/port-monitor"
LOG_FILE="$SCRIPT_DIR/monitor.log"
PID_FILE="$SCRIPT_DIR/monitor.pid"

# 检查是否已运行
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Port Monitor 已在运行 (PID: $PID)"
        exit 0
    fi
fi

# 启动监控（后台运行）
cd "$SCRIPT_DIR"
nohup python3 port_monitor.py --daemon > /dev/null 2>&1 &

# 保存 PID
echo $! > "$PID_FILE"
echo "Port Monitor 已启动 (PID: $(cat $PID_FILE))"
