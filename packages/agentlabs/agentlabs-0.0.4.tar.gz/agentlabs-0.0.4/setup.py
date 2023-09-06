"""
agentlabs: A Python libary for implementing agents on Weavel (https://weavel.vercel.app)
"""
from setuptools import setup, find_namespace_packages

# Read README.md for the long description
with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="agentlabs",
    version="0.0.4",
    packages=find_namespace_packages(),
    description="agentlabs: A Python library for implementing agents on Weavel",
    long_description=long_description,
    long_description_content_type="text/markdown",
    auther="weavel",
    install_requires=["pydantic"],
    python_requires=">=3.7.1",
    keywords=["weavel", "agent", "llm", "tools", "agentlabs", "llm agent"],
)
