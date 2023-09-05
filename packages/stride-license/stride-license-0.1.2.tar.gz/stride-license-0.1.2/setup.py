from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.1.2'
DESCRIPTION = 'Stride Licensing module for internal tools'
LONG_DESCRIPTION = 'A package that allows to encode, decode the data and generate license keys.'

setup(
    name="stride-license",
    version=VERSION,
    author="Sujith Dusa",
    author_email="<sujith.kumar@stride.ai>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[
        "cryptography"
    ]
)