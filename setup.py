from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kybra_simple_db",
    version="0.3.2",
    author="Smart Social Contracts",
    author_email="smartsocialcontracts@gmail.com",
    description="A lightweight key-value database with entity relationships and audit logging",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/smart-social-contracts/kybra-simple-db",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    install_requires=[],
)
