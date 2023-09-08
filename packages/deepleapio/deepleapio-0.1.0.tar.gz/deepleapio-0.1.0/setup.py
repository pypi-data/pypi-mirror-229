from setuptools import setup

# Read the project information from pyproject.toml
import toml

metadata = toml.load('pyproject.toml')['tool']['poetry']

setup(
    name=metadata['name'],
    version=metadata['version'],
    description=metadata['description'],
    author=metadata['authors'][0],
    packages=["deepleapio"],  
    install_requires=[
        "click==8.1.3",
        "colorama==0.4.6",
        "colorlog==6.7.0",
        "fastapi==0.88.0",
        "fastjsonschema==2.16.3",
        "jsonschema==4.17.3",
        "langchain==0.0.215",
        "openai==0.27.4",
        "prompt-toolkit==3.0.38",
        "pydantic==1.10.7",
        "python-dotenv==1.0.0",
        "qdrant-client==1.2.0",
        "threadpoolctl==3.1.0",
        "tiktoken==0.4.0",
        "uvicorn==0.21.1",
        "websocket-client==1.5.1",
        "websockets==11.0.3"
    ],
)
