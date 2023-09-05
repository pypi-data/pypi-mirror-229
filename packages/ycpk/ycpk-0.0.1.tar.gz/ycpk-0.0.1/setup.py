"""
Author: wind windzu1@gmail.com
Date: 2023-08-27 18:30:27
LastEditors: wind windzu1@gmail.com
LastEditTime: 2023-09-01 14:40:03
Description: 
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""
from setuptools import find_packages, setup


def parse_requirements(fname_list=[]):
    """Parse the package dependencies listed in a requirements list file."""
    requirements = []
    for fname in fname_list:
        with open(fname) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    requirements.append(line)
    # remove duplicates
    requirements = list(set(requirements))
    return requirements


# basic
setup(
    # 描述信息
    name="ycpk",
    version="0.0.1",
    description="yun chuang perception kit",
    author="windzu",
    author_email="windzu1@gmail.com",
    url="",
    license="MIT license",
    keywords="adas deeplearning",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    # 主要设置
    python_requires=">=3.6",
    packages=find_packages(exclude=("docs")),
    install_requires=parse_requirements(
        [
            "requirements/requirements.txt",
        ]
    ),
    entry_points={"console_scripts": ["ycpk=ycpk.main:main"]},
    # 次要设置
    include_package_data=True,
    zip_safe=False,
)
