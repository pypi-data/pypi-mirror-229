# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# This call to setup() does all the work
setup(
    name="df_preprocessor",
    version="1.1",
    description="library for pre-processingtools to apply on dataframes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Alix C., Claeys S., Herremy J.",
    author_email='',
    classifiers=[
        "Intended Audience :: Other Audience",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
    ],
    packages=["df_preprocessor"],
    include_package_data=True,
    install_requires=["pandas","plyer", "numpy"]
)