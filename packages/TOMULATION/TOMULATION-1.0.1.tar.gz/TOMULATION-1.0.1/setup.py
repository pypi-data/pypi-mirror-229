from setuptools import setup, find_packages
import TOMULATION

NAME = "TOMULATION"
AUTHOR = 'Naomichi Fujiuchi,Ryoga Maruko'
AUTHOR_EMAIL = 'wlingwo@gmail.com'
URL = 'https://github.com/marukory66/tomgrosim-on-pcse/tree/develop'
LICENSE = 'GPL3'
DOWNLOAD_URL = 'https://github.com/marukory66/tomgrosim-on-pcse/tree/develop'
VERSION = TOMULATION.__version__
DESCRIPTION = "TOMULATION: Predicts tomato yield using actual measured photosynthesis or photosynthesis predicted from environmental information."

long_description = "TOMULATION: Predicts tomato yield using actual measured photosynthesis or photosynthesis predicted from environmental information."

INSTALL_REQUIRES = [
    'pandas>=0.25']

CLASSIFIERS = [
    'Intended Audience :: Science/Research',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3 :: Only',
]

PACKAGES = ["TOMULATION"]

setup(name=NAME,
    author=AUTHOR,
    description= DESCRIPTION,
    long_description=long_description,
    author_email = AUTHOR_EMAIL,
    maintainer=AUTHOR,
    maintainer_email=AUTHOR_EMAIL,
    license=LICENSE,
    url=URL,
    version=VERSION,
    download_url=DOWNLOAD_URL,
    install_requires=INSTALL_REQUIRES,
    packages=PACKAGES,
    classifiers=CLASSIFIERS,
    )