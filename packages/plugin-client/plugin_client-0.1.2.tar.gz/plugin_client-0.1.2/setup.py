from setuptools import setup, find_packages

setup(
    name='plugin_client',
    version='0.1.2',
    url='',
    author='Luzhipeng',
    author_email='402087139@qq.com',
    description='Description of my package',
    packages=find_packages(),    
    install_requires=['websockets', 'openai', 'requests'],
)
