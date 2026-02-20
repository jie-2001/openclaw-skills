#!/usr/bin/env python3
"""
Port Checker - 定时端口检查脚本
用于 Cron 定时任务，发现问题发送到飞书
"""

import socket
import subprocess
import time
import sys
import os
from datetime import datetime

# 配置
CRITICAL_PORTS = [8188, 11434, 8080]  # 可在 config.json 中修改
CHECK_INTERVAL = 60  # 秒

# 服务名称
SERVICE_PORTS = {
    8188: "ComfyUI",
    11434: "Ollama API",
    8080: "Dify",
    5678: "N8N",
    8765: "Dify Upload",
    3306: "MySQL",
    6379: "Redis",
}

# 状态文件
STATUS_FILE = "/home/lhj/.openclaw/skills/port-monitor/.port_status"


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
    try:
        with open("/etc/resolv.conf", "r") as f:
            for line in f:
                if "nameserver" in line:
                    ip = line.split()[1]
                    if ip != "127.0.0.1" and check_port(ip, 8188):
                        return ip
    except:
        pass
    return "172.22.16.1"


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


def send_feishu(message):
    """发送飞书消息 - 输出到文件供外部处理"""
    print(message)
    # 写入消息队列文件
    msg_file = "/home/lhj/.openclaw/skills/port-monitor/.alert_queue"
    with open(msg_file, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()}|{message}\n")


def main():
    windows_ip = get_windows_ip()
    current_status = load_status()
    alerts = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
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
        message = f"""端口监控告警 - {timestamp}

{"".join(alerts)}

请检查服务是否正常运行。"""
        send_feishu(message)
        sys.exit(1)
    else:
        print(f"[{timestamp}] 端口状态正常")
        sys.exit(0)


if __name__ == "__main__":
    main()
