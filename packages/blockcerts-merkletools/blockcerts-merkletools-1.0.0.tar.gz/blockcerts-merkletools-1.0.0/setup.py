import os

from setuptools import find_packages
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

setup(
    name="blockcerts-merkletools",
    version="1.0.0",
    description="Merkle Tools",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    url="https://github.com/blockchain-certificates/blockcerts-pymerkletools",
    author='Blockcerts',
    author_email='info@blockcerts.org',
    keywords="merkle tree, blockchain",
    license="MIT",
    packages=find_packages(exclude=["tests"]),
    include_package_data=False,
    zip_safe=False,
)
