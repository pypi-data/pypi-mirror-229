from setuptools import setup, find_packages

setup(
    name='mysqlclientpy',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'mysql-connector-python',
        'protobuf'
    ],
)