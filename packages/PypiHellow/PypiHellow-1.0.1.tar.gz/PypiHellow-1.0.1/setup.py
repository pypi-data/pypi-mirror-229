from setuptools import setup, find_packages

setup(
    name='PypiHellow',
    version='1.0.1',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
    ]
)