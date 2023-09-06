# Agentlabs

> Python library for implementing agents on [Weavel](https://weavel.vercel.app)

## Installation

```bash
pip install agentlabs
```

## Usage

```python
from agentlabs.agent import Agent

agent = Agent()


@agent.service(
    name="service_name",
    description="service_description",
)
def your_service():
    return {"key_1": "value_1", "key_2": "value_2"}


if __name__ == "__main__":
    agent.run(token="YOUR_TOKEN")

```
