"""
Sample setup.py file
"""
from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\\n" + fh.read()

setup(
    name="declare4py",
    version='0.0.0.2',
    author="Ivan Donadello",
    author_email="donadelloivan@gmail.com",
    description="Python library to perform discovery, conformance checking and query checking of DECLARE constraints.",
    url = "https://github.com/ivanDonadello/Declare4Py",
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['numpy', 'pandas', 'pm4py', 'matplotlib', 'boolean.py', 'clingo'],
    keywords=['python', 'bpm', 'declare', 'process-mining', 'rule-mining', 'business-process-management', 'declarative-process-models'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows"
    ]
)
