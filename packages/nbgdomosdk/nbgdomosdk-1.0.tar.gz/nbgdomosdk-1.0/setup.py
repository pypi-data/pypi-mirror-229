# coding:utf-8
import sys

from setuptools import setup, find_packages

install_requires = [
    "requests>=2.25.1"
]

setup(
    name="nbgdomosdk",
    version=1.0,
    keywords=("pip", "nbgdomosdk", "nbg-demo-python-sdk"),
    description="The nbg demo SDK for Python",
    license="Apache Software License",

    url="https://github.com/newbeegpt/nbg-demo-python-sdk",
    author="newbeegpt",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=install_requires,
    classifiers=(
                "Development Status :: 4 - Beta",
                "Intended Audience :: Developers",
                "License :: OSI Approved :: Apache Software License",
                "Programming Language :: Python",
                "Programming Language :: Python :: 2.7",
                "Programming Language :: Python :: 3",
                "Programming Language :: Python :: 3.3",
                "Programming Language :: Python :: 3.4",
                "Programming Language :: Python :: 3.5",
                "Programming Language :: Python :: 3.6",
                "Programming Language :: Python :: 3.7",
                "Programming Language :: Python :: 3.8",
                "Programming Language :: Python :: 3.9",
                "Topic :: Software Development",
    )
)
