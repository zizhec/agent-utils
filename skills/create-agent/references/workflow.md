# create-agent 工作流程详解

## 完整流程图

```
┌─────────────────────────────────────────────────────────────┐
│                     开始创建 Agent                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 1: 收集人格信息（交互式9问）                           │
│  ├─ Agent ID（验证唯一性）                                   │
│  ├─ 显示名称                                                 │
│  ├─ 角色定位                                                 │
│  ├─ 核心使命                                                 │
│  ├─ 行为风格                                                 │
│  ├─ 特殊能力                                                 │
│  ├─ 边界限制                                                 │
│  ├─ 沟通风格                                                 │
│  └─ 记忆需求                                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 2: 收集技术配置                                        │
│  ├─ 模型选择（从可用列表选择）                               │
│  ├─ 通道绑定（可选）                                         │
│  │   ├─ 通道类型：whatsapp/telegram/discord/...             │
│  │   ├─ 账号 ID                                              │
│  │   └─ 特定 Peer（可选）                                    │
│  └─ 提及模式（群聊触发词）                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 3: 生成配置文件                                        │
│  ├─ 创建 JSON 配置                                           │
│  └─ 展示给用户确认                                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 4: 执行创建（自动化脚本）                              │
│  ├─ 验证 Agent ID                                            │
│  ├─ 创建工作区目录                                           │
│  ├─ 生成人格文件                                             │
│  │   ├─ SOUL.md                                              │
│  │   ├─ AGENTS.md                                            │
│  │   └─ USER.md                                              │
│  ├─ 创建 Agent（openclaw agents add）                        │
│  ├─ 应用配置补丁（config.patch）                             │
│  └─ 重启 Gateway                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 5: 验证                                                │
│  ├─ 检查 Agent 列表                                          │
│  ├─ 检查绑定配置                                             │
│  └─ 发送测试消息（可选）                                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     创建完成 ✓                               │
└─────────────────────────────────────────────────────────────┘
```

## 详细步骤说明

### Step 1: 人格设计问答

#### Q1: Agent ID
- **格式**: 小写字母、数字、连字符
- **限制**: 不能以连字符开头/结尾，不能是 `main`
- **示例**: `profitter`, `my-assistant`, `coder-bot`

#### Q2: 显示名称
- **用途**: 在 Agent 列表和消息中显示
- **示例**: `Profitter`, `My Assistant`, `代码助手`

#### Q3-9: 人格描述
根据用户的自然语言描述，提炼成结构化的配置字段。

### Step 2: 技术配置

#### 模型选择
运行 `openclaw models list` 获取可用模型列表，让用户选择。

#### 通道绑定（可选）
如果用户不想绑定通道，Agent 仍然可以：
- 通过 `sessions_spawn` 被其他 Agent 调用
- 在 Web UI 中使用
- 通过 API 调用

### Step 3: 配置生成

生成两个文件：
1. **临时 JSON 配置** - 用于脚本创建
2. **配置补丁** - 用于应用到 openclaw.json

### Step 4: 执行创建

脚本 `create_agent.py` 执行以下操作：

```python
# 1. 验证
validate_agent_id(agent_id)
check_agent_exists(agent_id)

# 2. 创建工作区
mkdir ~/.openclaw/workspace-{agent_id}/
mkdir ~/.openclaw/workspace-{agent_id}/memory/

# 3. 生成文件
write SOUL.md
write AGENTS.md
write USER.md

# 4. 创建 Agent
openclaw agents add {agent_id} \
  --workspace ~/.openclaw/workspace-{agent_id} \
  --model {model} \
  [--bind {channel}:{account_id}] \
  --non-interactive

# 5. 应用补丁
openclaw gateway call config.patch --params '{patch_json}'

# 6. 重启
openclaw gateway restart
```

### Step 5: 验证

```bash
# 验证 Agent 存在
openclaw agents list | grep {agent_id}

# 验证绑定
openclaw agents bindings | grep {agent_id}

# 验证工作区文件
ls ~/.openclaw/workspace-{agent_id}/
```

## 错误处理流程

```
错误发生
    │
    ├─→ 可恢复错误（如配置冲突）
    │   └─→ 提示用户修改配置，重试
    │
    ├─→ 严重错误（如权限不足）
    │   └─→ 回滚已创建的内容
    │   └─→ 报告错误，退出
    │
    └─→ 警告（如验证失败）
        └─→ 继续，但提示用户手动检查
```

## 回滚机制

如果创建过程中失败，自动回滚：

```python
try:
    create_agent(config)
except Exception as e:
    # 回滚
    if workspace_created:
        delete_workspace(agent_id)
    if agent_created:
        delete_agent(agent_id)
    raise
```
