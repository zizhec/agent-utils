---
name: create-agent
description: "Create a new OpenClaw Agent with full persona, workspace, and configuration. One-click automation for agent creation including personality files (SOUL.md, AGENTS.md, USER.md), technical setup, and channel bindings. Trigger: create agent, new agent, 创建agent, 创建机器人"
---

# create-agent

一键创建完整的 OpenClaw Agent，包含人格设计、工作区设置和技术配置。

## 功能

- **人格设计**: 交互式问答生成 SOUL.md、AGENTS.md、USER.md
- **技术配置**: 自动创建 Agent、绑定通道、设置模型
- **跨平台**: 支持 Windows、macOS、Linux
- **完整验证**: 创建后自动验证配置

## 使用方式

### 方式1：交互式（推荐）

直接告诉我你想创建什么 Agent，我会通过问答收集信息：

```
用户: 创建一个赚钱探索的 Agent
我: 好的，让我问你几个问题...
```

### 方式2：配置文件

准备 JSON 配置文件，然后运行脚本：

```bash
python scripts/create_agent.py --config agent_config.json
```

## 工作流程

### Step 1: 人格设计（9个问题）

1. **Agent ID** - 英文小写，如 `profitter`, `my-assistant`
2. **显示名称** - 如 `Profitter`, 我的小助手`
3. **角色定位** - 一句话描述你是谁
4. **核心使命** - 存在的意义是什么
5. **行为风格** - 如何行动、决策
6. **特殊能力** - 擅长什么
7. **边界限制** - 什么不能做
8. **沟通风格** - 如何与人交流
9. **记忆需求** - 需要记住什么

### Step 2: 技术配置

- **模型选择** - 从可用模型列表中选择
- **通道绑定** - 可选：whatsapp/telegram/discord/...
- **提及模式** - 如何在群聊中触发

### Step 3: 自动执行

脚本自动完成：
1. 创建工作区目录
2. 生成人格文件
3. 创建 Agent 配置
4. 应用配置补丁
5. 验证创建结果

## 配置示例

### 最小配置

```json
{
  "agent_id": "my-agent",
  "display_name": "My Agent",
  "role_description": "一个乐于助人的AI助手",
  "mission": "帮助用户完成任务",
  "behavior": "主动、高效、可靠",
  "abilities": "使用各种工具完成任务",
  "boundaries": "不违反法律，不伤害他人",
  "communication_style": "简洁明了，直接回答",
  "memory_structure": "memory/ 目录下的文件",
  "closing_remark": "随时准备帮助你",
  "workflow": "按照 AGENTS.md 执行",
  "tools_guide": "根据需要使用工具",
  "success_criteria": "任务完成，用户满意",
  "model": "bailian/kimi-k2.5"
}
```

### 完整配置（带通道绑定）

```json
{
  "agent_id": "profitter",
  "display_name": "Profitter",
  "role_description": "一个不择手段探索赚钱路径的AI",
  "mission": "千方百计赚钱，探索不同路径，记录成功与失败",
  "behavior": "探索精神、记录一切、快速迭代",
  "abilities": "市场调研、数据分析、自动化执行",
  "boundaries": "不违反法律，不伤害他人",
  "communication_style": "直接、务实、数据驱动",
  "memory_structure": "memory/explorations/, memory/successes.md, memory/failures.md, memory/patterns.md",
  "closing_remark": "记住：你的价值在于发现别人看不到的路径",
  "workflow": "1.机会识别 → 2.探索执行 → 3.结果归档",
  "tools_guide": "优先使用 web_search 调研，exec 自动化，write/edit 管理项目",
  "success_criteria": "产生正收益、可复制、可规模化",
  "model": "bailian/kimi-k2.5",
  "channel": "webchat",
  "mention_patterns": ["@profitter", "profitter", "赚钱"],
  "tool_allow": ["read", "write", "edit", "exec", "web_search", "web_fetch"]
}
```

## 输出文件

创建完成后，工作区包含：

```
~/.openclaw/workspace-{agent_id}/
├── SOUL.md          # 核心人格和使命
├── AGENTS.md        # 工作方式和工具指南
├── USER.md          # 主人信息（模板）
└── memory/          # 记忆目录（可选）
```

## 验证

创建后自动验证：

```bash
openclaw agents list              # 确认 Agent 存在
openclaw agents bindings          # 确认绑定正确
openclaw gateway restart          # 重启生效
```

## 错误处理

| 错误 | 原因 | 解决 |
|------|------|------|
| Invalid agent ID | 包含非法字符 | 使用小写字母、数字、连字符 |
| Agent already exists | ID 已被占用 | 更换 ID |
| Model not found | 模型不存在 | 运行 `openclaw models list` 查看可用模型 |
| Channel not configured | 通道未设置 | 先配置通道账号 |

## 与 agentcreate skill 的区别

| 特性 | agentcreate | create-agent (本 skill) |
|------|------------|------------------------|
| 人格设计 | ❌ 无 | ✅ 完整交互式 |
| 跨平台 | ❌ macOS only | ✅ Windows/macOS/Linux |
| 依赖 | qclaw-openclaw wrapper | 无，直接用 openclaw CLI |
| 通道支持 | 飞书中心化 | 所有通道平等 |
| 自动化程度 | 半自动 | 全自动 |

## 相关资源

- [references/workflow.md](references/workflow.md) - 详细工作流程
- [references/examples.md](references/examples.md) - 配置示例
- scripts/create_agent.py - 自动化脚本
