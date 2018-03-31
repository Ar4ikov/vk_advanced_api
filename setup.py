from distutils.core import setup
import vk_advanced_api

setup(
    name='vk_advanced_api',
    version=vk_advanced_api.vkapi.__version__,
    requires=['requests', 'captcha_solver', 'lxml', 'parsel', 'pymitter'],
    install_requires=['requests', 'captcha_solver', 'lxml', 'parsel', 'pymitter'],
    packages=['vk_advanced_api'],
    url='https://github.com/Ar4ikov/vk_advanced_api',
    license='MIT License',
    author='Nikita Archikov',
    author_email='bizy18588@gmail.com',
    description='Simple to use OpenSource Lib for API VK',
    keywords='opensource vk api wrappper ar4ikov vkadvancedapi vk_advanced_api'

)
