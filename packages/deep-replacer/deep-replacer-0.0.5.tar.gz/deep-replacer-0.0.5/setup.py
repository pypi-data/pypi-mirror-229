from setuptools import setup
from setuptools import find_packages

name = "deep-replacer"
version = "0.0.5"

with open("README.md", "r") as fh:
    long_description = fh.read()

requires = ["pydantic"]

setup(
    name=name,
    version=version,
    author="Zairon Jacobs",
    author_email="zaironjacobs@gmail.com",
    description="Given a list, set, tuple or dictionary as data input, loop through the data and replace all values that are not a list, set, tuple or dictionary using a replace function.",
    long_description=long_description,
    url="https://github.com/zaironjacobs/deep-replacer",
    download_url=f"https://github.com/zaironjacobs/deep-replacer/archive/v{version}.tar.gz",
    keywords=["replace", "replacer", "deep"],
    packages=find_packages(),
    install_requires=requires,
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.10",
        "Natural Language :: English",
    ],
    python_requires=">=3",
)
