#!/usr/bin/env python

from setuptools import setup

import os

_version_file_path = os.path.join(os.path.dirname(__file__), 'vk_advanced_api', 'version')

with open(_version_file_path) as f:
    __version__ = f.readline().strip()

setup(
    name='vk_advanced_api',
    version=__version__,
    install_requires=['requests', 'captcha_solver', 'lxml', 'parsel', 'pymitter', 'flask'],
    packages=['vk_advanced_api'],
    package_data={'vk_advanced_api': ['version']},
    url='https://github.com/Ar4ikov/vk_advanced_api',
    license='MIT License',
    author='Nikita Archikov',
    author_email='bizy18588@gmail.com',
    description='Simple to use OpenSource Lib for API VK',
    keywords='opensource vk api wrappper ar4ikov vkadvancedapi vk_advanced_api'
)
