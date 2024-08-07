# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open("README.rst") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="pyTTRPGsimulator",
    version="0.0.1",
    description="A python Table Top RPG simulator",
    long_description=readme,
    author="Remi Necnor",
    author_email="remi.necnor@gmail.com",
    url="https://github.com/remi-rc/pyTTRPGsimulator",
    license=license,
    packages=find_packages(exclude=("tests")),
)
