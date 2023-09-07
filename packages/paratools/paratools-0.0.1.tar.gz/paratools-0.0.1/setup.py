# Basic setup.py template

from setuptools import setup, find_packages

description = """
A python library that lets you import Python code blocks from
your Obsidian PARA project into a python project. Write notes 
when researching and import than later without needing to have 
2 things open at once. Focus on your current studies!!!!
"""

setup(
    name="paratools",
    version="0.0.1",
    description=description,
    author="Peter Kouvaris",
    author_email="kouvaris.peter@gmail.com",
    packages=find_packages(),
    install_requires=["click==8.1.7"],
    entry_points={
        "console_scripts": [
            "paratools=paratools.cli:cli"
        ]
    }
)
