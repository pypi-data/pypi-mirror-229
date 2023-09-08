from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="nonpoisonous",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
    ],
    author="Romlin Group AB",
    author_email="hello@romlin.com",
    description="A nonpoisonous dataset",
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "nonpoisonous=nonpoisonous.main:main"
        ],
    }
)
