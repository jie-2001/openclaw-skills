#!/usr/bin/env python3
"""
纯脚本方式：检查并启动 Port Manager
完全不消耗 token
"""

import subprocess
import os
import time

def check_port(port):
    """检查端口是否在监听"""
    try:
        result = subprocess.run(
            ["ss", "-tuln"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return f":{port}" in result.stdout
    except:
        return False

def start_service():
    """启动服务"""
    try:
        os.chdir("/home/lhj/.openclaw/workspace/port_manager")
        subprocess.Popen(
            ["python3", "port_manager.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        return True
    except:
        return False

def main():
    port = 10086
    
    if not check_port(port):
        print(f"端口 {port} 未运行，正在启动...")
        if start_service():
            print(f"✅ Port Manager 已启动")
        else:
            print(f"❌ 启动失败")
    else:
        print(f"✅ Port Manager 已在运行")

if __name__ == "__main__":
    main()
