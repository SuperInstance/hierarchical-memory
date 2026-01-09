"""
Setup configuration for hierarchical-memory package.

This package provides a 4-tier hierarchical memory system for AI agents.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

# Read version from __init__.py
def get_version():
    init_path = os.path.join(os.path.dirname(__file__), 'hierarchical_memory', '__init__.py')
    if os.path.exists(init_path):
        with open(init_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"').strip("'")
    return '1.0.0'

setup(
    name='hierarchical-memory',
    version=get_version(),
    author='SuperInstance',
    author_email='contact@superinstance.ai',
    description='A 4-tier hierarchical memory system for AI agents',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/superinstance/hierarchical-memory',
    project_urls={
        'Bug Reports': 'https://github.com/superinstance/hierarchical-memory/issues',
        'Source': 'https://github.com/superinstance/hierarchical-memory',
        'Documentation': 'https://hierarchical-memory.readthedocs.io',
    },
    packages=find_packages(exclude=['tests', 'tests.*', 'examples', 'docs']),
    classifiers=[
        # Development Status
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',

        # Topic
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries :: Python Modules',

        # License
        'License :: OSI Approved :: MIT License',

        # Python Version
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',

        # Operating System
        'Operating System :: OS Independent',

        # Typing
        'Typing :: Typed',
    ],
    keywords='memory, ai, agent, hierarchical, cognitive, embeddings, vector-database, episodic, semantic',
    python_requires='>=3.7',

    # Core dependencies (required for basic functionality)
    install_requires=[
        'numpy>=1.19.0,<2.0.0',
    ],

    # Optional dependencies for extended functionality
    extras_require={
        # For vector embeddings and semantic search
        'embeddings': [
            'sentence-transformers>=2.2.0',
        ],

        # For ChromaDB backend
        'chromadb': [
            'chromadb>=0.4.0',
        ],

        # For FAISS backend
        'faiss': [
            'faiss-cpu>=1.7.0',
        ],

        # All optional dependencies
        'all': [
            'sentence-transformers>=2.2.0',
            'chromadb>=0.4.0',
            'faiss-cpu>=1.7.0',
        ],

        # Development dependencies
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'pytest-asyncio>=0.21.0',
            'black>=23.0.0',
            'mypy>=1.0.0',
            'flake8>=6.0.0',
            'isort>=5.12.0',
            'sphinx>=6.0.0',
            'sphinx-rtd-theme>=1.2.0',
            'sphinx-autodoc-typehints>=1.23.0',
        ],
    },

    # Package data
    package_data={
        'hierarchical_memory': [
            'py.typed',
            'data/*',
        ],
    },

    # Include package data in distribution
    include_package_data=True,

    # Zip safe
    zip_safe=False,

    # Entry points (CLI commands if any)
    entry_points={
        'console_scripts': [
            # Example: 'hierarchical-memory-cli=hierarchical_memory.cli:main',
        ],
    },
)
