from setuptools import find_packages, setup

with open("README.md", "r") as fh:
  long_description = fh.read()

setup(
    name = "ip_address",
    version = "1.5.0",
    author = "Thomas Dewitte",
    author_email = "thomasdewittecontact@gmail.com",
    license = "MIT",
    url = "https://github.com/dewittethomas/ip-address",
    
    description = "A module to fetch your public IP address",
    long_description = long_description,
    long_description_content_type = "text/markdown",

    package_dir = {"ip_address": "ip_address"},
    install_requires = [
        "requests>=2.28.1"
    ],

    packages = find_packages(),

    classifiers = [
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
)