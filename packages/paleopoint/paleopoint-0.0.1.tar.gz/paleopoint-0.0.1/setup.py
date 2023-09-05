from setuptools import setup
from setuptools import find_packages

'''with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()'''

setup(
    name="paleopoint",
    version="0.0.1",
    author="Bailong Zhao",
    author_email="bailongzhao@163.com",
    description="A package calculates location to paleopoint",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
