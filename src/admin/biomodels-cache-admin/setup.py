from setuptools import setup, find_packages

setup(
    name="biomodels-cache-admin",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "pytest>=7.4.0",
    ],
    python_requires=">=3.8",
    author="Shengyi",
    author_email="shengyi@uw.edu",
    description="A package for managing BioModels database cache",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sys-bio/AntimonyEditor/biomodels-cache-admin",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 