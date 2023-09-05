from setuptools import setup, find_packages

setup(
    name='RATS-PRO-4abn',
    version='1.0.0',
    description='Data collation Flask app for RATS PRO',
    author='Christoforos Lapathiotis',
    author_email='clapathiotis@gmail.com',
    packages=find_packages(),
    install_requires=[
        'Flask',
        'pandas',
        'requests',
        'requests-oauthlib'
    ],
)