from setuptools import setup, find_packages
import codecs
import os


VERSION = '0.0.1'
DESCRIPTION = 'Python package to encrypt data for Adyen payment processing'

# Setting up
setup(
    name="PyDatadome",
    version=VERSION,
    author="66niko99",
    author_email="niko@slimaio.com",
    description=DESCRIPTION,
    url="https://github.com/66niko99/PyDatadome",
    packages=find_packages(),
)

