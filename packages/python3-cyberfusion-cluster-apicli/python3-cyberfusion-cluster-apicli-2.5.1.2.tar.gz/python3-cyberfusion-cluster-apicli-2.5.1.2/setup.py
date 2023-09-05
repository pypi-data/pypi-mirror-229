"""A setuptools based setup module."""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="python3-cyberfusion-cluster-apicli",
    version="2.5.1.2",
    description="API client for Cluster API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.9",
    author="William Edwards",
    author_email="wedwards@cyberfusion.nl",
    url="https://vcs.cyberfusion.nl/core/python3-cyberfusion-cluster-apicli",
    platforms=["linux"],
    packages=["cyberfusion.ClusterApiCli"],
    data_files=[],
    package_dir={"": "src"},
    install_requires=[
        "python3-cyberfusion-common",
        "cached_property==1.5.2",
        "certifi==2020.6.20",
        "requests==2.25.1",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=["cyberfusion", "cluster", "api"],
    license="MIT",
)
