#!/usr/bin/env python3
"""
模型切换脚本
用于在模型切换时自动调整 session-memory hook 状态

功能：
1. 接收模型 ID 参数
2. 判断模型类型（本地/云端）
3. 读取当前 hook 状态
4. 根据模型类型调整 hook 状态

用法：
    python model_switcher.py <model_id>
    
示例：
    python model_switcher.py ollama/qwen3:30b
    python model_switcher.py minimax-portal/MiniMax-M2.5
"""

import json
import sys
import os

# 配置文件路径
CONFIG_PATH = os.path.expanduser("~/.openclaw/openclaw.json")

# 模型类型判断
LOCAL_MODEL_PREFIX = "ollama/"

def get_current_model():
    """获取当前使用的模型"""
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        primary_model = config.get('agents', {}).get('defaults', {}).get('model', {}).get('primary', '')
        return primary_model
    except Exception as e:
        print(f"Error reading config: {e}")
        return None

def get_hook_status():
    """获取当前 hook 状态"""
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        hook_enabled = config.get('hooks', {}).get('internal', {}).get('entries', {}).get('session-memory', {}).get('enabled', False)
        return hook_enabled
    except Exception as e:
        print(f"Error reading hook status: {e}")
        return None

def is_local_model(model_id):
    """判断是否为本地模型"""
    return model_id.startswith(LOCAL_MODEL_PREFIX)

def update_hook_status(enable_hook):
    """更新 hook 状态"""
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        
        # 设置 hook 状态
        if 'hooks' not in config:
            config['hooks'] = {}
        if 'internal' not in config['hooks']:
            config['hooks']['internal'] = {}
        if 'entries' not in config['hooks']['internal']:
            config['hooks']['internal']['entries'] = {}
        
        config['hooks']['internal']['entries']['session-memory'] = {
            'enabled': enable_hook
        }
        
        # 写回配置
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error updating hook status: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python model_switcher.py <model_id>")
        print("Example: python model_switcher.py ollama/qwen3:30b")
        sys.exit(1)
    
    target_model = sys.argv[1]
    
    # 获取当前状态
    current_model = get_current_model()
    current_hook_status = get_hook_status()
    
    print(f"=== 模型切换执行 ===")
    print(f"目标模型: {target_model}")
    print(f"当前模型: {current_model}")
    print(f"当前 Hook 状态: {'开启' if current_hook_status else '关闭'}")
    
    # 判断目标模型类型
    is_local = is_local_model(target_model)
    model_type = "本地模型" if is_local else "云端模型"
    print(f"目标模型类型: {model_type}")
    
    # 根据模型类型调整 hook
    if is_local:
        # 本地模型：关闭 hook
        new_hook_status = False
        action = "关闭"
    else:
        # 云端模型：开启 hook
        new_hook_status = True
        action = "开启"
    
    # 只有状态不一致时才更新
    if current_hook_status != new_hook_status:
        print(f"\n→ 调整 Hook 状态: {action}")
        success = update_hook_status(new_hook_status)
        if success:
            print(f"✅ Hook 已{action}（{model_type}）")
        else:
            print(f"❌ Hook 状态调整失败")
            sys.exit(1)
    else:
        print(f"\n→ Hook 状态无需调整（当前已是正确状态）")
    
    print(f"\n=== 执行完成 ===")

if __name__ == "__main__":
    main()
