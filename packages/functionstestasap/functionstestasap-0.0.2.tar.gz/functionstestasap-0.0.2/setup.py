
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="functionstestasap",                     # This is the name of the package
    version="0.0.2",                        # The initial release version
    author="TestNew",                     # Full name of the author
    description="Quicksample Test Package for SQLShack Demo",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),    # List of all python modules to be installed
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.6',                # Minimum version requirement of the package
    py_modules=["moduleOne", "moduleTwo"], 
    package_dir={'':'functions/src'},
    install_requires=[
        'datetime', 'openpyxl', 'xlrd'
    ],
)