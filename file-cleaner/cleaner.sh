#!/bin/bash

# File Cleaner Script
# 文件清理器 - 自动清理无用文件，智能识别需确认的文件

set -e

# 配置
AGENTS_DIR="$HOME/.openclaw/agents/main/sessions"
OPTIMIZED_DIR="$HOME/.openclaw/workspace/memory/optimized"
MEMORY_DIR="$HOME/.openclaw/workspace/memory"
LOGS_DIR="$HOME/.openclaw/logs"

# 清理配置
RETENTION_DAYS=30
LOG_RETENTION_DAYS=7

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_section() { echo -e "\n${BLUE}==== $1 ====${NC}\n"; }

# 获取文件年龄（天数）
get_file_age_days() {
  local file="$1"
  if [ -f "$file" ]; then
    local mtime=$(stat -c %Y "$file" 2>/dev/null || stat -f %m "$file" 2>/dev/null)
    local now=$(date +%s)
    echo $(( (now - mtime) / 86400 ))
  else
    echo "0"
  fi
}

# 检查是否有优化记忆
has_optimized_memory() {
  if [ -d "$OPTIMIZED_DIR" ] && [ "$(ls -A "$OPTIMIZED_DIR" 2>/dev/null)" ]; then
    return 0
  else
    return 1
  fi
}

# 显示存储状态
show_storage_status() {
  log_section "存储状态"
  
  local sessions_size=$(du -sh "$AGENTS_DIR" 2>/dev/null | awk '{print $1}' || echo "0")
  local sessions_count=$(ls -1 "$AGENTS_DIR"/*.jsonl 2>/dev/null | wc -l)
  
  local optimized_size="N/A"
  local optimized_count=0
  if [ -d "$OPTIMIZED_DIR" ]; then
    optimized_size=$(du -sh "$OPTIMIZED_DIR" 2>/dev/null | awk '{print $1}' || echo "0")
    optimized_count=$(ls -1 "$OPTIMIZED_DIR"/*.md 2>/dev/null | wc -l)
  fi
  
  local logs_size=$(du -sh "$LOGS_DIR" 2>/dev/null | awk '{print $1}' || echo "0")
  
  echo "📊 当前存储使用情况:"
  echo "  - sessions/: $sessions_size ($sessions_count 个文件)"
  echo "  - optimized/: $optimized_size ($optimized_count 个文件)"
  echo "  - logs/: $logs_size"
  echo ""
}

# 自动清理函数
auto_clean() {
  log_section "自动清理"
  
  local total_freed=0
  
  # 1. 清理过期的 session 文件
  log_info "检查过期 session 文件..."
  local expired_count=0
  local expired_size=0
  
  for f in "$AGENTS_DIR"/*.jsonl; do
    if [ -f "$f" ]; then
      local age=$(get_file_age_days "$f")
      if [ "$age" -gt "$RETENTION_DAYS" ]; then
        local size=$(stat -c %s "$f" 2>/dev/null || stat -f %z "$f" 2>/dev/null)
        expired_size=$((expired_size + size))
        expired_count=$((expired_count + 1))
      fi
    fi
  done
  
  if [ "$expired_count" -gt 0 ]; then
    local size_mb=$(echo "scale=2; $expired_size / 1024 / 1024" | bc)
    log_info "发现 $expired_count 个过期文件 (可释放 ${size_mb}MB)"
    
    for f in "$AGENTS_DIR"/*.jsonl; do
      if [ -f "$f" ]; then
        local age=$(get_file_age_days "$f")
        if [ "$age" -gt "$RETENTION_DAYS" ]; then
          rm -f "$f"
          log_info "已删除: $(basename "$f")"
        fi
      fi
    done
    total_freed=$((total_freed + expired_size))
  else
    log_info "无过期文件需要清理"
  fi
  
  # 2. 清理临时文件
  log_info "检查临时文件..."
  local temp_count=0
  local temp_size=0
  
  # 查找临时文件
  for f in "$AGENTS_DIR"/*.tmp; do
    if [ -f "$f" ]; then
      local size=$(stat -c %s "$f" 2>/dev/null || echo 0)
      temp_size=$((temp_size + size))
      rm -f "$f"
      temp_count=$((temp_count + 1))
    fi
  done
  
  if [ "$temp_count" -gt 0 ]; then
    local size_kb=$(echo "scale=2; $temp_size / 1024" | bc)
    log_info "已删除 $temp_count 个临时文件 (释放 ${size_kb}KB)"
    total_freed=$((total_freed + temp_size))
  fi
  
  # 3. 如果有优化记忆，标记原文件可清理
  if has_optimized_memory; then
    log_info "检测到优化记忆，原始 session 文件可安全清理"
  fi
  
  # 显示总计
  if [ $total_freed -gt 0 ]; then
    local total_mb=$(echo "scale=2; $total_freed / 1024 / 1024" | bc)
    echo ""
    log_info "✅ 自动清理完成，共释放 ${total_mb}MB"
  else
    echo ""
    log_info "✅ 无需自动清理"
  fi
}

# 待确认清理函数
confirm_clean() {
  log_section "待确认清理"
  
  local confirm_count=0
  local files_to_check=()
  
  # 检查 7-30 天的文件
  log_info "检查需要确认的文件..."
  
  for f in "$AGENTS_DIR"/*.jsonl; do
    if [ -f "$f" ]; then
      local age=$(get_file_age_days "$f")
      # 7-30 天的文件需要确认
      if [ "$age" -ge 7 ] && [ "$age" -le "$RETENTION_DAYS" ]; then
        local size=$(du -h "$f" | awk '{print $1}')
        local date=$(stat -c %y "$f" 2>/dev/null | cut -d' ' -f1 || echo "unknown")
        files_to_check+=("$(basename "$f")|$size|${age}天前")
        confirm_count=$((confirm_count + 1))
      fi
    fi
  done
  
  if [ "$confirm_count" -eq 0 ]; then
    log_info "无需要确认的文件"
    return
  fi
  
  echo "❓ 以下文件需要您确认处理方式:\n"
  
  local index=1
  for item in "${files_to_check[@]}"; do
    IFS='|' read -r filename size age <<< "$item"
    echo "$index. $filename"
    echo "   大小: $size | 时间: $age"
    echo "   操作: [保留] [删除] [以后不清理]"
    echo ""
    index=$((index + 1))
  done
  
  echo "请逐个告诉我每个文件的处理方式"
  echo "或说'全部保留'/'全部删除'"
}

# 主程序
main() {
  show_storage_status
  auto_clean
  confirm_clean
}

main "$@"
