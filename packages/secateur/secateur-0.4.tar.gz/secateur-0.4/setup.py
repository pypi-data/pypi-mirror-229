from setuptools import setup, find_packages

doc = '''
## Introduction
...

## Installation / Requirements
...

## Documentation
...

## Getting Help / Development / Bug reporting
Please create an issue on <https://github.com/darentydarenty/secateur/issues>

## License
Secateur is distributed under the [MIT License](https://opensource.org/license/mit/).
'''

requirements = ["SQLAlchemy>=2.0.20", "prettytable>=3.8.0", "jaal>=0.1.5"]

setup(
    name="secateur",
    version="0.4",
    description="The Database Shrink Toolkit for Python, SQLAlchemy addon",
    long_description=doc,
    long_description_content_type="text/markdown",
    author="Daniil Somov",
    author_email="bearscream3@gmail.com",
    url="https://github.com/darentydarenty/secateur",
    packages=find_packages(),
    install_requires=requirements,
)