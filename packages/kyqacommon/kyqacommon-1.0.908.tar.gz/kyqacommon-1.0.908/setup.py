# -*- coding: utf-8 -*-

import setuptools  # 导入setuptools打包工具

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kyqacommon",  # 包名
    version="1.0.908",  # 包版本号，便于维护版本
    author="lyl",  # 作者
    author_email="lyulei66@163.com",  # 联系方式
    description="kyqacommon",  # 包的简述
    long_description=long_description,  # 包的详细介绍，一般在README.md文件内
    long_description_content_type="text/markdown",
    url="",  # 自己项目地址，比如github的项目地址
    packages=setuptools.find_packages(),
    install_requires = ["minio==7.1.13","pymysql==1.0.3","progress==1.6","paramiko==3.2.0"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # 对python的最低版本要求
)
'''
Python setup.py sdist bdist_wheel
Python -m twine upload --repository pypi dist/*
'''
