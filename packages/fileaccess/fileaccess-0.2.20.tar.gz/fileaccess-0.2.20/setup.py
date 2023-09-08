from setuptools import setup, find_packages

setup(
    name="fileaccess",
    version="0.2.20",
    packages=find_packages(),
    install_requires=[
    ],
    author="Joe Hacobian",
    author_email="joehacobian@gmail.com",
    description="A package for easier file access, automatically closes opened file handles, & provides for simple file/directory creation.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/node0/Fileaccess",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
