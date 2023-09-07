from setuptools import setup, find_packages
import os

setup(
    name="astrotransform",
    version="0.1.3",
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
    classifiers=[
    'Development Status :: 3 - Alpha',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
],
)
