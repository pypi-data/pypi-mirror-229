from setuptools import setup, find_packages

setup(
    name="sawsi",
    version="1.01",
    packages=find_packages(),
    install_requires=[
        'boto3==1.28.43'
    ],
)
