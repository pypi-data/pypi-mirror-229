
import setuptools
from setuptools import setup,find_packages

with open("README.md","r",encoding="utf-8") as desc:
    longDesc = desc.read()
classifier = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent"
]

setup(
    name="pyLense",
    version="0.0.1",
    author="The Neurals",
    description="This is a simple url/link checker API",
    long_description=longDesc,
    long_description_content_type = "text/markdown",
    url="https://t.me/Neuralp",
    classifiers=classifier,
    packages=find_packages(),
    keywords=["url ckeck","link check","link","url"],
    python_requires=">=3.6",
    py_modules=["pyLense"]

)