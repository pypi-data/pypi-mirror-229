"""
agentlabs: A Python libary for implementing agents on Weavel (https://weavel.vercel.app)
"""
from setuptools import setup, find_namespace_packages

setup(
    name="agentlabs",
    version="0.0.3",
    packages=find_namespace_packages(),
    description="agentlabs: A Python library for implementing agents on Weavel (https://weavel.vercel.app)",
    auther="weavel",
    install_requires=["pydantic"],
    python_requires=">=3.7.1",
    keywords=["weavel", "agent", "llm", "tools", "agentlabs", "llm agent"],
)
