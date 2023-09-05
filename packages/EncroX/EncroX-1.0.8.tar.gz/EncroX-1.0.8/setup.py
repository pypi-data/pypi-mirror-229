from setuptools import setup

setup(
    name='EncroX',
    version='1.0.8',
    packages=['EncroX'],
    url='https://github.com/KindLittleTurtle/EncroX',
    license='AGPL3.0',
    author='核善的小兲',
    author_email='hsdxt@mwtour.cn',
    description='EncroX是一个强大的加密拓展工具，旨在为您的应用程序和系统提供可靠的加密和解密功能。通过集成各种密码学算法和密钥管理方法，EncroX使您能够轻松地进行数据加密、解密和安全通信。',
    install_requires=['cryptography'],
    long_description=open(r'C:\EncroX\README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    package_data={
        'EncroX': ['*.pyi']
    }
)
