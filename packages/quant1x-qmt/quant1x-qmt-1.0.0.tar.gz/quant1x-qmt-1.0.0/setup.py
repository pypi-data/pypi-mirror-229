#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""The setup script."""

try:
    from setuptools import find_packages, setup
except ImportError:
    from distutils.core import find_packages, setup


def parse_requirements(filename):
    line_iter = (line.strip() for line in open(filename))
    return [line for line in line_iter if line and not line.startswith("#")]


with open("README.rst", encoding="utf-8") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst", encoding="utf-8") as history_file:
    history = history_file.read()

requirements = parse_requirements("requirements.txt")
test_requirements = requirements

from qmt import __version__, __author__

setup(
    name="quant1x-qmt",
    description="Quant1X程序化交易系统",
    author_email="wangfengxy@sina.cn",
    url="https://gitee.com/quant1x/qmt",
    version=__version__,
    author=__author__,
    long_description=readme,
    packages=find_packages(include=["qmt", "xtquant","xtquant.*"]),
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords="qmt",
    entry_points={
        "console_scripts": [
            "qmt=qmt.__main__:main",
        ]
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    # # 安装过程中，需要安装的静态文件，如配置文件、service文件、图片等
    # data_files=[
    #     # ('', ['conf/*.conf']),
    #     #('xtquant', ['*.dll','xtquant/*.pyd','xtquant/*.ini','xtquant/*.log4cxx']),
    # ],
    #
    # # 希望被打包的文件
    # package_data={
    #     #'': ['*.*'],
    # },
    # # 不打包某些文件
    # exclude_package_data={
    #     # 'bandwidth_reporter': ['*.txt']
    # },
    test_suite="tests",
    tests_require=test_requirements,
    setup_requires=requirements,
)
