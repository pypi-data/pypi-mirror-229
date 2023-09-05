import logging

from setuptools import *


setup(
    name='cbutil',
    version='1.2.6',
    packages=find_namespace_packages('inc'),
    package_dir={'cbutil': 'inc/cbutil'},
    install_requires=[
        'base58',
        'more_itertools'
        ],
    python_requires='>=3.8',

    url='https://github.com/happyxianyu/cbutil-python',
    license='Apache License 2.0',
    author='happyxianyu',
    author_email=' happyxianyu623@outlook.com',
    description='Utility Library'
)

