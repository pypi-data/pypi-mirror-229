#!/usr/bin/env python
from pathlib import Path
this_directory = Path(__file__).parent

if __name__ == "__main__":
    import setuptools
    long_description = "\n".join([
        open("README.rst").read(),
    ])
    setuptools.setup(
        keywords=['SMS', 'SEND SMS', 'Universal SMS', 'Django SMS'],
        long_description=long_description,
        long_description_content_type='text/markdown'
    )
