# Lib
from setuptools import setup, find_packages

# Read dependencies from requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Setup
setup(
    name='fdr-beta',
    version='0.1.0',
    description='Sample fdr lib',
    author='Konstantinos Gyftodimos',
    author_email='c.gyftodimos@gmail.com',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'fdr = client.main:fdr_client',
        ],
    },
    install_requires=requirements,
    password='stws',
)
