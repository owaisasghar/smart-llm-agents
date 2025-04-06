from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='llm_agents',
    version='1.0.0',
    description='Advanced framework for building intelligent agents powered by Large Language Models (LLMs)',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Awais Asghar',
    author_email='awaisasghar900@gmail.com',
    url='https://github.com/owaisasghar/llm-agents',
    packages=find_packages(),
    install_requires=[
        'openai>=1.0.0',
        'pydantic>=2.0.0',
        'numpy>=1.24.0',
        'scikit-learn>=1.2.0',
        'sentence-transformers>=2.2.0',
        'aiohttp>=3.8.0',
        'python-dotenv>=1.0.0',
        'requests>=2.28.0',
        'beautifulsoup4>=4.12.0',
        'langchain>=0.1.0',
        'tiktoken>=0.4.0',
        'tenacity>=8.2.0',
        'asyncio>=3.4.3'
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0',
            'black>=23.0.0',
            'isort>=5.12.0',
            'mypy>=1.0.0'
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.8',
    keywords='llm, agent, ai, nlp, machine-learning, artificial-intelligence',
    project_urls={
        'Documentation': 'https://github.com/owaisasghar/llm-agents#readme',
        'Source': 'https://github.com/owaisasghar/llm-agents',
        'Tracker': 'https://github.com/owaisasghar/llm-agents/issues',
    },
)
