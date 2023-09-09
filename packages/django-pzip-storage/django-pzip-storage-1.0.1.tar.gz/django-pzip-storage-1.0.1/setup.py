import re

from setuptools import setup

with open("README.md", "r") as readme:
    long_description = readme.read()

with open("pzip_storage.py", "r") as src:
    version = re.match(r'.*__version__ = "(.*?)"', src.read(), re.S).group(1)

setup(
    name="django-pzip-storage",
    version=version,
    description="Storage backend for Django that encrypts/compresses with PZip.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Dan Watson",
    author_email="watsond@imsweb.com",
    url="https://github.com/imsweb/django-pzip-storage",
    license="MIT",
    py_modules=["pzip_storage"],
    install_requires=["pzip>=0.9.9"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
)
