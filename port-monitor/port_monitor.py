#!/usr/bin/env python3
"""
Port Monitor - 端口持续监控 + 飞书告警
支持 WSL 和 Windows 端口监控，端口断开时自动发送飞书提醒
"""

import os
import sys
import json
import socket
import subprocess
import threading
import time
import argparse
import signal
from datetime import datetime
from pathlib import Path

# 配置路径
SKILL_DIR = Path(__file__).parent
CONFIG_FILE = SKILL_DIR / "config.json"
LOG_FILE = SKILL_DIR / "monitor.log"

# 默认配置
DEFAULT_CONFIG = {
    "check_interval": 30,
    "critical_ports": [8188, 11434, 8080],
    "notification_enabled": True,
    "wsl_ip": "auto",
    "windows_ip": "auto",
    "notify_on_recover": False  # 端口恢复时是否通知
}

# 常用服务端口映射
SERVICE_PORTS = {
    22: "SSH",
    80: "HTTP",
    443: "HTTPS",
    3000: "Node.js",
    3306: "MySQL",
    5432: "PostgreSQL",
    5678: "N8N",
    6379: "Redis",
    8080: "Dify",
    8188: "ComfyUI",
    8765: "Dify Upload",
    11434: "Ollama API",
    27017: "MongoDB",
    5000: "Win 进程管理",
    5003: "ComfyUI/N8N",
    8000: "Django",
    8888: "Jupyter",
    9090: "Prometheus",
    9200: "Elasticsearch",
    2375: "Docker",
    2376: "Docker TLS",
}


class PortMonitor:
    def __init__(self, config):
        self.config = config
        self.running = True
        self.port_status = {}  # 存储端口状态 {"port": {"status": "UP"/"DOWN", "last_check": time}}
        self.wsl_ip = None
        self.windows_ip = None
        
        # 初始化所有端口状态为 UNKNOWN
        for port in self.config.get("critical_ports", []):
            self.port_status[port] = {"status": "UNKNOWN", "last_check": None}
        
    def get_local_ip(self):
        """获取 WSL IP"""
        try:
            result = subprocess.run(
                ["hostname", "-I"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.stdout:
                return result.stdout.strip().split()[0]
        except:
            pass
        return "127.0.0.1"
    
    def get_windows_ip(self):
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
                            if self._check_port_reachable(gw, 8188):
                                return gw
        except:
            pass
        # 备用方法
        try:
            with open("/etc/resolv.conf", "r") as f:
                for line in f:
                    if "nameserver" in line:
                        ip = line.split()[1]
                        if ip != "127.0.0.1" and self._check_port_reachable(ip, 8188):
                            return ip
        except:
            pass
        return "172.22.16.1"
    
    def _check_port_reachable(self, ip, port, timeout=1):
        """检查端口是否可达"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def get_service_name(self, port):
        """获取服务名称"""
        return SERVICE_PORTS.get(port, f"Port-{port}")
    
    def log(self, message):
        """日志输出"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        
        # 写入日志文件
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log_msg + "\n")
        except:
            pass
    
    def send_feishu_notification(self, port, status, ip):
        """发送飞书通知"""
        if not self.config.get("notification_enabled", True):
            return
        
        service_name = self.get_service_name(port)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if status == "DOWN":
            # 端口断开告警
            message = f"""🔴 端口告警

端口 {port} ({service_name}) 已断开！
检测时间: {current_time}
目标地址: {ip}:{port}

请检查服务是否正常运行。"""
        else:
            # 端口恢复通知（可选）
            if not self.config.get("notify_on_recover", False):
                return
            message = f"""✅ 端口恢复

端口 {port} ({service_name}) 已恢复！
检测时间: {current_time}
目标地址: {ip}:{port}"""
        
        # 调用飞书 webhook（需要配置）
        self._send_webhook(message)
    
    def _send_webhook(self, message):
        """发送飞书机器人消息"""
        # 从环境变量或配置文件获取 webhook 地址
        webhook_url = os.environ.get("FEISHU_WEBHOOK_URL", "")
        
        if not webhook_url:
            # 尝试从配置文件读取
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    webhook_url = config.get("feishu_webhook", "")
            except:
                pass
        
        if not webhook_url:
            self.log("⚠️ 未配置飞书 Webhook，跳过通知")
            return
        
        try:
            import requests
            payload = {"msg_type": "text", "content": {"text": message}}
            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.status_code == 200:
                self.log(f"✅ 飞书通知发送成功")
            else:
                self.log(f"❌ 飞书通知发送失败: {response.status_code}")
        except ImportError:
            self.log("⚠️ 需要安装 requests 库才能发送飞书通知")
        except Exception as e:
            self.log(f"❌ 飞书通知发送失败: {e}")
    
    def check_port(self, ip, port):
        """检查单个端口状态"""
        is_reachable = self._check_port_reachable(ip, port)
        status = "UP" if is_reachable else "DOWN"
        
        old_status = self.port_status.get(port, {}).get("status", "UNKNOWN")
        
        # 状态变化检测
        if old_status != "UNKNOWN" and old_status != status:
            self.log(f"⚡ 端口 {port} 状态变化: {old_status} → {status}")
            # 发送通知（仅在 DOWN 时发送，避免频繁通知）
            if status == "DOWN":
                self.send_feishu_notification(port, status, ip)
        
        self.port_status[port] = {
            "status": status,
            "last_check": time.time()
        }
        
        return status
    
    def init_ips(self):
        """初始化 IP 地址"""
        wsl_ip_config = self.config.get("wsl_ip", "auto")
        windows_ip_config = self.config.get("windows_ip", "auto")
        
        self.wsl_ip = self.get_local_ip() if wsl_ip_config == "auto" else wsl_ip_config
        self.windows_ip = self.get_windows_ip() if windows_ip_config == "auto" else windows_ip_config
        
        self.log(f"📡 WSL IP: {self.wsl_ip}")
        self.log(f"📡 Windows IP: {self.windows_ip}")
    
    def run(self):
        """主监控循环"""
        self.init_ips()
        self.log("🚀 端口监控服务启动")
        self.log(f"📋 监控端口: {self.config.get('critical_ports', [])}")
        self.log(f"⏱️ 检测间隔: {self.config.get('check_interval', 30)}秒")
        
        while self.running:
            try:
                critical_ports = self.config.get("critical_ports", [])
                
                for port in critical_ports:
                    # 判断端口属于 WSL 还是 Windows
                    # 默认检查 Windows 端口（大多数服务在 Windows 上）
                    target_ip = self.windows_ip
                    
                    # 检查端口状态
                    status = self.check_port(target_ip, port)
                    status_icon = "✅" if status == "UP" else "❌"
                    service = self.get_service_name(port)
                    self.log(f"{status_icon} 端口 {port} ({service}): {status}")
                
                # 等待下一次检测
                interval = self.config.get("check_interval", 30)
                for _ in range(interval):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                self.log("🛑 收到中断信号，正在停止...")
                break
            except Exception as e:
                self.log(f"❌ 监控出错: {e}")
                time.sleep(5)
        
        self.log("👋 端口监控服务已停止")
    
    def stop(self):
        """停止监控"""
        self.running = False


def load_config():
    """加载配置文件"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                # 合并默认配置
                merged = DEFAULT_CONFIG.copy()
                merged.update(config)
                return merged
        except Exception as e:
            print(f"⚠️ 配置文件读取失败: {e}")
    
    # 创建默认配置
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
    
    return DEFAULT_CONFIG


def send_to_feishu(message):
    """发送消息到当前飞书会话"""
    try:
        # 使用 OpenClaw 的消息发送功能
        # 通过环境变量或配置文件获取 session info
        import requests
        
        # 尝试从配置获取飞书 webhook
        webhook_url = os.environ.get("FEISHU_WEBHOOK_URL", "")
        if not webhook_url:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                webhook_url = config.get("feishu_webhook", "")
        
        if webhook_url:
            payload = {"msg_type": "text", "content": {"text": message}}
            requests.post(webhook_url, json=payload, timeout=10)
    except Exception as e:
        print(f"⚠️ 发送飞书消息失败: {e}")


def main():
    parser = argparse.ArgumentParser(description="Port Monitor - 端口监控 + 飞书告警")
    parser.add_argument("--no-notification", action="store_true", help="禁用飞书通知")
    parser.add_argument("--interval", type=int, help="检测间隔（秒）")
    parser.add_argument("--critical", type=str, help="重点端口，逗号分隔，如: 8188,11434,8080")
    parser.add_argument("--daemon", action="store_true", help="后台运行模式")
    args = parser.parse_args()
    
    # 加载配置
    config = load_config()
    
    # 命令行参数覆盖配置
    if args.no_notification:
        config["notification_enabled"] = False
    
    if args.interval:
        config["check_interval"] = args.interval
    
    if args.critical:
        try:
            config["critical_ports"] = [int(p.strip()) for p in args.critical.split(",")]
        except ValueError:
            print("❌ 端口格式错误，请使用逗号分隔的数字")
            sys.exit(1)
    
    # 后台运行模式
    if args.daemon:
        # fork 进程
        try:
            pid = os.fork()
            if pid > 0:
                # 父进程退出
                sys.exit(0)
        except OSError as e:
            print(f"❌ Fork 失败: {e}")
            sys.exit(1)
        
        # 脱离终端
        os.chdir("/")
        os.setsid()
        os.umask(0)
        
        # 第二次 fork
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError:
            sys.exit(1)
        
        # 重定向标准输出
        sys.stdout.flush()
        sys.stderr.flush()
        with open("/dev/null", "r") as f:
            os.dup2(f.fileno(), sys.stdin.fileno())
        with open("/dev/null", "a+") as f:
            os.dup2(f.fileno(), sys.stdout.fileno())
            os.dup2(f.fileno(), sys.stderr.fileno())
    
    # 创建监控实例
    monitor = PortMonitor(config)
    
    # 信号处理
    def signal_handler(sig, frame):
        print("\n")
        monitor.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动监控
    monitor.run()


if __name__ == "__main__":
    main()
