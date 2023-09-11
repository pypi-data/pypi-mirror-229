from setuptools import setup, find_packages

setup(
    name="biblepy",
    license="MIT",
    url="https://github.com/johnnysands/bible",
    author="Johnny Sands",
    author_email="johnnysands@users.noreply.github.com",
    version="0.1.1",
    description="The Bible, King James Version",
    packages=find_packages(),
    package_data={"kjv": ["data/*.jsonl"]},
    readme="README.md",
)
