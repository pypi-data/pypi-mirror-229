# Agentlabs

> Python library for implementing agents on [Weavel](https://weavel.vercel.app)

## Installation

```bash
pip install agentlabs
```

## Example Usage

```python
from agentlabs.agent import Agent

agent = Agent()


@agent.service(
    id=10,
    name="blog_post",
    description="Given a keyword as input, this service generates a SEO-optimized blog post",
)
@agent.service_input(
    name="keyword",
    display_name="키워드",
    description="The keyword for which the blog post should be generated",
    type="string",
)
def generate_blog(keyword: str):
    agent.update_status("Generating blog outline...")
    agent.update_status("Writing post...")
    agent.update_status("Searching for images...")
    agent.update_status("Adding images to post...")
    agent.update_status("Generating title...")
    return {
        "blog": "블로그",
    }


if __name__ == "__main__":
    agent.run(token="5f7598e7-1a10-492e-a9c1-e7521d403e2b")

```
