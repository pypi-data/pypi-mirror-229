from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.1'
DESCRIPTION = 'BSenti: Sentiment Classification Library'
LONG_DESCRIPTION = 'This library provide a unique way to access different sentiment classification datasets and create sentiment classification liberaries based on the datasets.'

# Setting up
setup(
    name="BSenti",
    version=VERSION,
    author="Saadat (Saadat Rafid Ahmed)",
    author_email="<saadat.r.ahmed@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['pandas', 'joblib', 'scikit-learn'],
    keywords=['python', 'sentiment classification', 'nlp'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
