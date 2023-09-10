# -*- coding: utf-8 -*-
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

PACKAGE_DIR = 'src'

setuptools.setup(
    name="ipylib",
    version="0.3.1",
    author="innovata",
    author_email="iinnovata@gmail.com",
    description='Pure Python3 기능을 재사용하기 위해 한단계 추상화된 라이브러리 패키지',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/innovata/iPyLibrary",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"":PACKAGE_DIR},
    packages=setuptools.find_packages(PACKAGE_DIR),
    python_requires=">=3.8",
)
