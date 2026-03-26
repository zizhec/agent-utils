#!/bin/bash
# Claude Code 环境变量加载脚本 (Linux/macOS/Git Bash)

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# SCRIPT_DIR="$HOME/.claude/script"
ENV_FILE="$SCRIPT_DIR/.env.claude.profiles"

if [ ! -f "$ENV_FILE" ]; then
    echo "错误: 找不到配置文件 '$ENV_FILE'"
    return 1 2>/dev/null || exit 1
fi

echo "正在加载配置文件: $ENV_FILE"
echo "----------------------------------------"

# 读取ALL_VARS定义
ALL_VARS=$(grep "^ALL_VARS=" "$ENV_FILE" | cut -d'=' -f2-)
# 去除引号
ALL_VARS=$(echo "$ALL_VARS" | sed 's/^["'"'"']//;s/["'"'"']$//')
IFS=',' read -ra ALL_VAR_ARRAY <<< "$ALL_VARS"

# 解析所有profile名称
PROFILES=()
PROFILE_VARS=()  # 每个profile对应的变量

current_profile=""
current_vars=""

while IFS= read -r line || [ -n "$line" ]; do
    # 跳过空行和注释行
    [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue

    # 去除行首尾空白
    line=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

    # 检查是否是profile标记 [profile_name]
    if [[ "$line" =~ ^\[([a-zA-Z0-9_]+)\]$ ]]; then
        # 保存上一个profile的变量
        if [ -n "$current_profile" ]; then
            PROFILES+=("$current_profile")
            PROFILE_VARS+=("$current_vars")
        fi
        current_profile="${BASH_REMATCH[1]}"
        current_vars=""
    elif [[ -n "$current_profile" && "$line" =~ ^([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]]; then
        key="${BASH_REMATCH[1]}"
        value="${BASH_REMATCH[2]}"
        # 去除值两边的引号（如果有）
        value=$(echo "$value" | sed 's/^["'"'"']//;s/["'"'"']$//')
        current_vars="$current_vars$key=$value"$'\n'
    fi
done < "$ENV_FILE"

# 保存最后一个profile
if [ -n "$current_profile" ]; then
    PROFILES+=("$current_profile")
    PROFILE_VARS+=("$current_vars")
fi

# 显示profile选项
echo ""
echo "请选择要加载的 Profile:"
echo "----------------------------------------"
for i in "${!PROFILES[@]}"; do
    echo "  [$i] ${PROFILES[$i]}"
done
echo "----------------------------------------"
echo -n "请输入数字编号: "
read -r choice

# 验证输入
if ! [[ "$choice" =~ ^[0-9]+$ ]] || [ "$choice" -ge ${#PROFILES[@]} ]; then
    echo "错误: 无效的选择"
    return 1 2>/dev/null || exit 1
fi

selected_profile="${PROFILES[$choice]}"
selected_vars="${PROFILE_VARS[$choice]}"

echo ""
echo "已选择 Profile: $selected_profile"
echo "----------------------------------------"

# 首先清空所有ALL_VARS中的变量
for var in "${ALL_VAR_ARRAY[@]}"; do
    unset "$var" 2>/dev/null
done

# 加载选中的profile的变量
LOADED_VARS=()
while IFS= read -r line || [ -n "$line" ]; do
    [ -z "$line" ] && continue
    key="${line%%=*}"
    value="${line#*=}"
    export "$key=$value"
    LOADED_VARS+=("$key")
done <<< "$selected_vars"

echo ""
echo "已设置的环境变量:"
echo "----------------------------------------"
for var in "${LOADED_VARS[@]}"; do
    value="${!var}"
    # 对敏感信息进行掩码处理
    if [[ "$var" == *"TOKEN"* || "$var" == *"KEY"* || "$var" == *"SECRET"* ]]; then
        if [ ${#value} -gt 8 ]; then
            masked="${value:0:4}****${value: -4}"
        else
            masked="****"
        fi
        echo "  $var=$masked"
    else
        echo "  $var=$value"
    fi
done
echo "----------------------------------------"
echo "共加载 ${#LOADED_VARS[@]} 个环境变量"
echo ""
echo "现在可以运行: claude"
