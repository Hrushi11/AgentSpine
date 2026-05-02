---
title: Getting Started
description: Quick installation and setup for AgentSpine SDK.
---

AgentSpine is an adaptive control plane for production AI agents. This guide will help you get up and running with the SDK in minutes.

## Installation

You can install the AgentSpine SDK directly from PyPI:

```bash
pip install agentspine
```

If you need Redis support for high-performance deduplication, install with the optional dependency:

```bash
pip install "agentspine[redis]"
```

## Prerequisites

AgentSpine requires:
- **Python 3.11+**
- **Postgres 16+** (Primary state store)
- **Redis 7+** (Optional, for deduplication and caching)

### Rapid Local Setup

If you have Docker installed, you can start the required infrastructure with a single command using our provided compose file:

```bash
# Clone the repository
git clone https://github.com/Hrushi11/AgentSpine.git
cd AgentSpine

# Start Postgres and Redis
docker compose up -d postgres redis
```

## Quick Start Code

Here is a minimal example of using the AgentSpine SDK to track a task execution:

```python
import asyncio
from agentspine import AgentSpine

async def main():
    # Initialize the spine for a specific workflow
    spine = AgentSpine(workflow="customer_onboarding")
    
    # Track a task execution
    result = await spine.execute_task(
        task_id="onboard_user_123",
        action="send_welcome_email",
        params={"email": "user@example.com"}
    )
    
    print(f"Task status: {result.status}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Next Steps

Now that you have AgentSpine running, explore these topics:

- [Detailed Configuration](/AgentSpine/configuration/)
- [Core Architecture Concepts](/AgentSpine/concepts/)
- [Pipeline Model](/AgentSpine/pipeline/)
