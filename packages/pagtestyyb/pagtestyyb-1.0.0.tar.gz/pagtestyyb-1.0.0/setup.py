#!/usr/bin python3
# -*- encoding: utf-8 -*-
# @Author : yunlong
# Email : yunlong@fudata.cn
# @File : setup.py.py
# @Time : 2023/9/6 3:46 下午

from setuptools import setup

setup(name='pagtestyyb',
  version='1.0.0',
  description='A print test for PyPI',
  author='winycg',
  author_email='1064804095@qq.com',
  url='https://www.python.org/',
  license='MIT',
  keywords='ga nn',
  project_urls={
   'Documentation': 'https://packaging.python.org/tutorials/distributing-packages/',
   'Funding': 'https://donate.pypi.org',
   'Source': 'https://github.com/pypa/sampleproject/',
   'Tracker': 'https://github.com/pypa/sampleproject/issues',
  },
  packages=['pagtestyyb'],
  install_requires=['numpy>=1.14'],
  python_requires='>=3'
  )