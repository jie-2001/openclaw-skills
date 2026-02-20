#!/usr/bin/env python3
"""
纯脚本方式：检查重点端口状态
完全不消耗 token，有异常时发送飞书消息
"""

import socket
import subprocess
import time
import os
from datetime import datetime

# 配置
CRITICAL_PORTS = [8188, 11434, 8080]  # 重点端口列表
WINDOWS_IP = "172.22.16.1"  # Windows IP
CHECK_INTERVAL = 60  # 秒

# 服务名称
SERVICE_PORTS = {
    8188: "ComfyUI",
    11434: "Ollama API",
    8080: "Dify",
}

STATUS_FILE = "/home/lhj/.openclaw/skills/port-monitor/.port_status"
ALERT_QUEUE = "/home/lhj/.openclaw/skills/port-monitor/.alert_queue"

def get_windows_ip():
    """获取 Windows IP"""
    try:
        result = subprocess.run(
            ["ip", "route", "show", "default"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.stdout:
            for line in result.stdout.split('\n'):
                if 'default' in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        gw = parts[2]
                        if check_port(gw, 8188):
                            return gw
    except:
        pass
    return WINDOWS_IP

def check_port(ip, port, timeout=1):
    """检查端口是否可达"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

def load_status():
    """加载上次状态"""
    if os.path.exists(STATUS_FILE):
        try:
            import json
            with open(STATUS_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {}

def save_status(status):
    """保存状态"""
    import json
    os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f)

def send_alert(message):
    """发送告警到队列"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ALERT_QUEUE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def main():
    windows_ip = get_windows_ip()
    current_status = load_status()
    alerts = []
    
    for port in CRITICAL_PORTS:
        is_up = check_port(windows_ip, port)
        status = "UP" if is_up else "DOWN"
        service = SERVICE_PORTS.get(port, f"Port-{port}")
        
        # 检测状态变化
        old_status = current_status.get(str(port), "UNKNOWN")
        
        if old_status != "UNKNOWN" and old_status != status:
            if status == "DOWN":
                alerts.append(f"🔴 端口告警: {port} ({service}) 已断开！")
        
        current_status[str(port)] = status
    
    # 保存状态
    save_status(current_status)
    
    # 发送告警
    if alerts:
        message = f"端口监控告警\n" + "\n".join(alerts)
        send_alert(message)
        print(f"⚠️ 告警: {alerts}")
    else:
        print(f"✅ 端口状态正常")

if __name__ == "__main__":
    main()
