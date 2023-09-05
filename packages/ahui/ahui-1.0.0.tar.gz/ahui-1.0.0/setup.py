# -*- coding: utf-8 -*-
from setuptools import setup,find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = 'ahui',         # 包名(pip install name)
    version = '1.0.0',     # 版本号
    description = '企业微信群机器人消息推送应用',  # 包的简述
    readme = 'README.md',
    long_description = long_description,         # 包的详细描述，从README.md文件中读取
    long_description_content_type = 'text/markdown',  # 包的详细描述的格式
    author = '阿辉',     # 作者
    author_email ='ahui6888@126.com',   # 作者邮箱
    url = 'https://github.com/ahui',    # 项目地址(github)
    packages = find_packages(),   # 自动查找包含的包列表
    python_requires = '>=3.6',    # Python的最低版本要求
    install_requires = [          # 安装依赖的包(若已安装最新版的库则跳过，否则默认安装最新版/升级老版本)
        'pandas',
        'requests',
        'Pillow'],
    classifiers = [    # 包的分类标签
        'Programming Language :: Python :: 3',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
        ]
    )
