from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.1'
DESCRIPTION = 'A package for Adaptive Spatio-Temporal Model (AdaSTEM) in python'
LONG_DESCRIPTION = 'stemflow is a toolkit for Adaptive Spatio-Temporal Model (AdaSTEM) in python. A typical usage is daily abundance estimation using eBird citizen science data. It leverages the "adjacency" information of surrounding target values in space and time, to predict the classes/continues values of target spatial-temporal point. In the demo, we use a two-step hurdle model as "base model", with XGBoostClassifier for occurence modeling and XGBoostRegressor for abundance modeling.'

# Setting up
setup(
    name="stemflow",
    version=VERSION,
    author="Yangkang Chen",
    author_email="chenyangkang24@outlook.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[''],
    keywords=['python', 'spatial-temporal model', 'ebird', 'citizen science', 'spatial temporal exploratory model',
              'STEM','AdaSTEM','abundance','phenology'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)