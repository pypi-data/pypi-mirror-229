from setuptools import setup, find_packages

setup(
    name='fdr-dev6',
    version='0.1.0',
    description='Sample fdr lib',
    author='Konstantinos Gyftodimos',
    author_email='konstgyftodimos@gmail.com',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'fdr = client.main:fdr_client',
        ],
    },
)
