from setuptools import setup, find_packages
import os

setup(
    name="AstroTransform",
    version="0.1",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        'numpy>=1.14.0',
        'datetime>=4.0.0',
    ],
    author="David Law",
    author_email="d.j.law@2021.ljmu.ac.uk",
    description="Package for astronomical transformations and calculations.",
    long_description=open('README.md', 'r').read() if 'README.md' in os.listdir() else "",
    long_description_content_type="text/markdown",
)
