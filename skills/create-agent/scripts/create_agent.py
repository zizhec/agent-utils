#!/usr/bin/env python3
"""
create-agent: One-click Agent creation for OpenClaw
Creates a new Agent with full persona, workspace, and configuration.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


def get_openclaw_cmd():
    """Get the openclaw command for current platform."""
    if sys.platform == "win32":
        return "openclaw"
    return "openclaw"


def run_openclaw(args: List[str], check=True) -> subprocess.CompletedProcess:
    """Run openclaw command."""
    cmd = [get_openclaw_cmd()] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise Exception(f"Command failed: {' '.join(cmd)}\nError: {result.stderr}")
    return result


def validate_agent_id(agent_id: str) -> bool:
    """Validate agent ID format."""
    if not agent_id:
        return False
    # Only lowercase letters, numbers, and hyphens
    if not re.match(r'^[a-z0-9-]+$', agent_id):
        return False
    # Cannot start or end with hyphen
    if agent_id.startswith('-') or agent_id.endswith('-'):
        return False
    # Cannot be 'main'
    if agent_id == 'main':
        return False
    return True


def check_agent_exists(agent_id: str) -> bool:
    """Check if agent already exists."""
    try:
        result = run_openclaw(["agents", "list"], check=False)
        return agent_id in result.stdout
    except:
        return False


def get_available_models() -> List[str]:
    """Get list of available models."""
    try:
        result = run_openclaw(["models", "list"])
        # Parse output to extract model names
        models = []
        for line in result.stdout.split('\n'):
            if '/' in line and not line.startswith(' '):
                model = line.strip().split()[0] if line.strip() else None
                if model:
                    models.append(model)
        return models if models else ["bailian/kimi-k2.5"]
    except:
        return ["bailian/kimi-k2.5"]


def generate_soul_md(config: Dict) -> str:
    """Generate SOUL.md content."""
    return f"""# SOUL.md - {config['display_name']}

_你是 {config['display_name']}，{config['role_description']}_

## 核心使命

{config['mission']}

## 行为准则

{config['behavior']}

## 特殊能力

{config['abilities']}

## 边界限制

{config['boundaries']}

## 沟通风格

{config['communication_style']}

## 记忆系统

你的记忆存储在：
{config['memory_structure']}

---

_{config['closing_remark']}_
"""


def generate_agents_md(config: Dict) -> str:
    """Generate AGENTS.md content."""
    return f"""# AGENTS.md - {config['display_name']} 操作指南

## 工作流程

{config['workflow']}

## 工具使用指南

{config['tools_guide']}

## 记录模板

### 新项目启动
```markdown
# 项目名称: [名称]

## 目标
[一句话描述]

## 执行计划
1. [步骤1]
2. [步骤2]

## 状态
[未开始/进行中/已完成]
```

## 成功标准

{config['success_criteria']}

## 持续改进

定期回顾并更新本文件。
"""


def generate_user_md(config: Dict) -> str:
    """Generate USER.md content."""
    return f"""# USER.md - 关于你的主人

_记录主人的信息，以便更好地服务。_

- **名称**: [待填写]
- **称呼**: [待填写]
- **时区**: [待填写]

## 背景

- **专业领域**: [待填写]
- **可用时间**: [待填写]
- **可用资源**: [待填写]

## 目标

- **短期目标**: [待填写]
- **长期目标**: [待填写]

## 偏好

- **沟通方式**: [待填写]
- **报告频率**: [待填写]

---

_主人可以编辑此文件来更新信息。_
"""


def create_agent_config(config: Dict) -> Dict:
    """Create agent configuration for openclaw.json."""
    agent_config = {
        "id": config['agent_id'],
        "name": config['display_name'],
        "workspace": str(Path.home() / f".openclaw/workspace-{config['agent_id']}"),
        "agentDir": str(Path.home() / f".openclaw/agents/{config['agent_id']}/agent"),
        "model": {
            "primary": config['model']
        }
    }
    
    # Add group chat mention patterns if specified
    if config.get('mention_patterns'):
        agent_config['groupChat'] = {
            "mentionPatterns": config['mention_patterns']
        }
    
    # Add tool restrictions if specified
    if config.get('tool_allow'):
        agent_config['tools'] = {
            "allow": config['tool_allow']
        }
    
    return agent_config


def create_binding_config(config: Dict) -> Optional[Dict]:
    """Create binding configuration."""
    if not config.get('channel'):
        return None
    
    binding = {
        "agentId": config['agent_id'],
        "match": {
            "channel": config['channel']
        }
    }
    
    if config.get('account_id'):
        binding['match']['accountId'] = config['account_id']
    
    if config.get('peer_id'):
        binding['match']['peer'] = {
            "kind": "direct",
            "id": config['peer_id']
        }
    
    return binding


def create_agent(config: Dict) -> Dict:
    """Main function to create agent."""
    results = {
        "success": False,
        "steps": [],
        "errors": []
    }
    
    try:
        agent_id = config['agent_id']
        
        # Step 1: Validate agent ID
        if not validate_agent_id(agent_id):
            raise ValueError(f"Invalid agent ID: {agent_id}. Use lowercase letters, numbers, and hyphens only.")
        
        if check_agent_exists(agent_id):
            raise ValueError(f"Agent '{agent_id}' already exists.")
        
        results['steps'].append("✓ Agent ID validated")
        
        # Step 2: Create workspace directory
        workspace = Path.home() / f".openclaw/workspace-{agent_id}"
        workspace.mkdir(parents=True, exist_ok=False)
        
        # Create memory subdirectory
        memory_dir = workspace / "memory"
        memory_dir.mkdir()
        
        results['steps'].append(f"✓ Created workspace: {workspace}")
        
        # Step 3: Generate personality files
        soul_content = generate_soul_md(config)
        with open(workspace / "SOUL.md", "w", encoding="utf-8") as f:
            f.write(soul_content)
        
        agents_content = generate_agents_md(config)
        with open(workspace / "AGENTS.md", "w", encoding="utf-8") as f:
            f.write(agents_content)
        
        user_content = generate_user_md(config)
        with open(workspace / "USER.md", "w", encoding="utf-8") as f:
            f.write(user_content)
        
        results['steps'].append("✓ Generated personality files (SOUL.md, AGENTS.md, USER.md)")
        
        # Step 4: Create agent via CLI
        cmd_args = [
            "agents", "add", agent_id,
            "--workspace", str(workspace),
            "--model", config['model'],
            "--non-interactive"
        ]
        
        if config.get('channel') and config.get('account_id'):
            cmd_args.extend(["--bind", f"{config['channel']}:{config['account_id']}"])
        
        run_openclaw(cmd_args)
        results['steps'].append(f"✓ Created agent '{agent_id}' via CLI")
        
        # Step 5: Update config with additional settings
        agent_config = create_agent_config(config)
        binding_config = create_binding_config(config)
        
        # Generate patch config
        patch = {
            "agents": {
                "list": [agent_config]
            }
        }
        
        if binding_config:
            patch["bindings"] = [binding_config]
        
        results['config_patch'] = json.dumps(patch, indent=2, ensure_ascii=False)
        results['steps'].append("✓ Generated configuration patch")
        
        # Step 6: Verify
        result = run_openclaw(["agents", "list"], check=False)
        if agent_id in result.stdout:
            results['steps'].append(f"✓ Verified agent '{agent_id}' exists")
            results['success'] = True
        else:
            results['warnings'] = [f"Agent created but not found in list. May need manual verification."]
        
        results['workspace'] = str(workspace)
        results['agent_id'] = agent_id
        
    except Exception as e:
        results['errors'].append(str(e))
        results['success'] = False
    
    return results


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Create a new OpenClaw Agent')
    parser.add_argument('--config', '-c', required=True, help='Path to config JSON file')
    parser.add_argument('--dry-run', '-d', action='store_true', help='Show what would be done without executing')
    
    args = parser.parse_args()
    
    # Load config
    with open(args.config, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    if args.dry_run:
        print("=== DRY RUN MODE ===")
        print(f"Would create agent: {config.get('agent_id')}")
        print(f"With config: {json.dumps(config, indent=2, ensure_ascii=False)}")
        return
    
    # Create agent
    results = create_agent(config)
    
    # Output results as JSON
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    # Exit with appropriate code
    sys.exit(0 if results['success'] else 1)


if __name__ == '__main__':
    main()