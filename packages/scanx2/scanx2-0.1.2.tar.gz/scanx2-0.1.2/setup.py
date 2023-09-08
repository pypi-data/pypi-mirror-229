from setuptools import setup, find_packages

setup(
    name='scanx2',
    version='0.1.2',
    author='scannerx',
    author_email='dastscannerx@gmail.com',
    description='Web Vulnerability Scanner X2',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)