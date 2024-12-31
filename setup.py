from setuptools import setup, find_packages

# Read the requirements from requirements.txt
with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setup(
    name="qifutils",
    version="0.1.0",
    description="A utility package for parsing and visualizing QIF (Quicken Interchange Format) contents",
    author="Graham Schelle",
    author_email="your.email@example.com",
    url="https://github.com/schelleg/qifutils", 
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)