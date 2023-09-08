from setuptools import setup, find_packages

setup(
    name='cryptomind',
    version='0.0',
    author= 'istakshaydilip',
    description= 'Cryptomind is a tool to interact between different cryptocurrencies.',
    long_description=open('README.md').read(),
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'cryptomind=cryptomind.main:main',
        ],
    },
)
