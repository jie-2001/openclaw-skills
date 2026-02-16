#!/bin/bash

# Memory Optimizer Script
# 记忆优化器 - 自动压缩过长的对话记忆

set -e

# 配置参数
AGENTS_DIR="$HOME/.openclaw/agents/main/sessions"
OPTIMIZED_DIR="$HOME/.openclaw/workspace/memory/optimized"
MEMORY_DIR="$HOME/.openclaw/workspace/memory"

# 阈值配置
THRESHOLD_KB=50
THRESHOLD_MESSAGES=100

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 检查是否有 jq（可选）
check_dependencies() {
  if ! command -v jq &> /dev/null; then
    log_warn "jq 未安装，将使用简化模式"
    HAS_JQ=false
  else
    HAS_JQ=true
  fi
}

# 获取对话总大小
get_total_size_kb() {
  local total=$(du -sk "$AGENTS_DIR" 2>/dev/null | awk '{print $1}')
  echo "${total:-0}"
}

# 获取对话消息数量（简单统计行数）
get_total_messages() {
  local count=0
  for f in "$AGENTS_DIR"/*.jsonl; do
    if [ -f "$f" ]; then
      local line_count=$(wc -l < "$f" 2>/dev/null || echo "0")
      count=$((count + line_count))
    fi
  done
  echo "$count"
}

# 获取最新的优秀记忆
get_latest_optimized() {
  if [ -d "$OPTIMIZED_DIR" ] && [ "$(ls -A "$OPTIMIZED_DIR" 2>/dev/null)" ]; then
    ls -t "$OPTIMIZED_DIR"/optimized-*.md 2>/dev/null | head -1
  else
    echo ""
  fi
}

# 解析优秀记忆中的对话列表
get_optimized_sessions() {
  local opt_file="$1"
  if [ -f "$opt_file" ]; then
    grep -E "^- session-" "$opt_file" 2>/dev/null | sed 's/^- session-//' | cut -d':' -f1 || echo ""
  fi
}

# 提取对话关键信息
extract_key_info() {
  local session_file="$1"
  
  # 提取用户消息
  jq -r 'select(.type == "message" and .message.role == "user") | .message.content[]? | select(.type == "text") | .text' "$session_file" 2>/dev/null | head -20
  
  # 提取助手回复中的关键决策
  jq -r 'select(.type == "message" and .message.role == "assistant") | .message.content[]? | select(.type == "text") | .text' "$session_file" 2>/dev/null | grep -E "(已记录|已设置|记住|好的)" | head -10
}

# 创建优秀记忆
create_optimized_memory() {
  local output_file="$OPTIMIZED_DIR/optimized-$(date +%Y-%m-%d).md"
  
  mkdir -p "$OPTIMIZED_DIR"
  
  log_info "创建优秀记忆文件: $output_file"
  
  # 收集所有 session 的关键信息
  {
    echo "# 优秀记忆 - $(date +%Y-%m-%d)"
    echo ""
    echo "## 组成对话"
    
    for f in "$AGENTS_DIR"/*.jsonl; do
      if [ -f "$f" ]; then
        local session_id=$(basename "$f" .jsonl)
        local first_msg=$(jq -r 'select(.type == "message" and .message.role == "user") | .message.content[]? | select(.type == "text") | .text' "$f" 2>/dev/null | head -1)
        echo "- session-$session_id: $first_msg"
      fi
    done
    
    echo ""
    echo "## 关键信息"
    
    # 提取用户名称相关
    for f in "$AGENTS_DIR"/*.jsonl; do
      if [ -f "$f" ]; then
        jq -r 'select(.type == "message" and .message.role == "user") | .message.content[]? | select(.type == "text") | .text' "$f" 2>/dev/null | grep -iE "(我叫|叫我|名字|name)" | head -3
      fi
    done
    
    echo ""
    echo "## 重要规则"
    
    # 提取规则设置
    for f in "$AGENTS_DIR"/*.jsonl; do
      if [ -f "$f" ]; then
        jq -r 'select(.type == "message" and .message.role == "assistant") | .message.content[]? | select(.type == "text") | .text' "$f" 2>/dev/null | grep -iE "(已记录|已设置|已保存|规则|记住)" | head -5
      fi
    done
    
    echo ""
    echo "---"
    echo "创建时间: $(date -Iseconds)"
    echo "总对话数: $(get_total_messages)"
    echo "总大小: $(get_total_size_kb)KB"
    
  } > "$output_file"
  
  log_info "优秀记忆创建完成: $output_file"
  echo "$output_file"
}

# 读取记忆（带优化）
read_optimized_memory() {
  local latest_opt=$(get_latest_optimized)
  
  if [ -n "$latest_opt" ] && [ -f "$latest_opt" ]; then
    log_info "读取优秀记忆: $latest_opt"
    cat "$latest_opt"
    
    # TODO: 检查并读取未收录的后续对话
    log_info "如需完整上下文，请告知"
  else
    log_warn "无优秀记忆，读取全部对话"
    
    # 读取所有对话
    for f in "$AGENTS_DIR"/*.jsonl; do
      if [ -f "$f" ]; then
        echo "=== $(basename "$f") ==="
        jq -r 'select(.type == "message") | .message.role: .message.content[]? | select(.type == "text") | .text' "$f" 2>/dev/null | head -20
      fi
    done
  fi
}

# 检查是否需要优化
check_optimization_needed() {
  local size_kb=$(get_total_size_kb)
  local msg_count=$(get_total_messages)
  
  log_info "当前对话状态:"
  echo "  - 总大小: ${size_kb}KB"
  echo "  - 消息数: ${msg_count}条"
  
  if [ "$size_kb" -gt $((THRESHOLD_KB * 1024)) ]; then
    log_warn "对话大小超过 ${THRESHOLD_KB}MB 阈值，建议优化"
    return 0
  elif [ "$msg_count" -gt $THRESHOLD_MESSAGES ]; then
    log_warn "对话消息超过 ${THRESHOLD_MESSAGES}条 阈值，建议优化"
    return 0
  else
    log_info "对话大小适中，无需优化"
    return 1
  fi
}

# 主菜单
show_menu() {
  echo "========================================"
  echo "       Memory Optimizer - 记忆优化器"
  echo "========================================"
  echo ""
  echo "1. 检查是否需要优化"
  echo "2. 创建优秀记忆"
  echo "3. 读取记忆（带优化）"
  echo "4. 查看优秀记忆列表"
  echo "5. 退出"
  echo ""
}

# 主程序
main() {
  check_dependencies
  
  # 创建优化目录
  mkdir -p "$OPTIMIZED_DIR"
  
  # 如果有参数，执行相应操作
  case "${1:-menu}" in
    check)
      check_optimization_needed
      ;;
    create)
      create_optimized_memory
      ;;
    read)
      read_optimized_memory
      ;;
    list)
      ls -la "$OPTIMIZED_DIR"/
      ;;
    *)
      # 交互模式
      while true; do
        show_menu
        read -p "请选择操作 [1-5]: " choice
        case $choice in
          1) check_optimization_needed ;;
          2) create_optimized_memory ;;
          3) read_optimized_memory ;;
          4) ls -la "$OPTIMIZED_DIR"/ ;;
          5) exit 0 ;;
          *) log_error "无效选择" ;;
        esac
        echo ""
      done
      ;;
  esac
}

main "$@"
