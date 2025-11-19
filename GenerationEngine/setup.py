"""
Setup configuration for R-Gen Generation Engine
"""

from setuptools import setup, find_packages
import os

# Read README for long description
readme_path = os.path.join(os.path.dirname(__file__), '..', 'README.md')
if os.path.exists(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()
else:
    long_description = "Procedural content generation for fantasy worlds"

setup(
    name="rgen-generation-engine",
    version="1.0.0",
    author="R-Gen Team",
    description="Procedural content generation for fantasy worlds",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['data/*.json'],
    },
    install_requires=[
        "numpy>=1.19.0",
    ],
    extras_require={
        'database': ['psycopg2-binary>=2.8.0'],
        'web': ['flask>=2.0.0', 'flask-cors>=3.0.10'],
        'all': ['psycopg2-binary>=2.8.0', 'flask>=2.0.0', 'flask-cors>=3.0.10'],
    },
    python_requires='>=3.7',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    entry_points={
        'console_scripts': [
            'rgen-generate=cli:main',
        ],
    },
)
