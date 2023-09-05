from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

VERSION = '0.1'
DESCRIPTION = 'Natural Language processing package'

# Setting up
setup(
    name="PyNlProcessor",
    version=VERSION,
    author="Pranav Adibatla",
    author_email="<adpranav05@gmail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['pandas','scikit-learn','nltk'],
    keywords=['python', 'Natural Language Processing', 'vectorization', 'Machine Learnig'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
