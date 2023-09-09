from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.3'
DESCRIPTION = 'The Ultimate URL Masking Tool'
LONG_DESCRIPTION = 'Facad1ng is an open-source URL masking tool designed to help you Hide Phishing URLs and make them look legit using social engineering techniques.'

# Setting up
setup(
    name="Facad1ng",
    version=VERSION,
    author="Spyboy",
    author_email="<spyboyblog@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    Homepage= "https://github.com/spyboy-productions/Facad1ng",
    install_requires=['pyshorteners', 'argparse'],
    keywords=['masking', 'phishing', 'url-shortener', 'mask-phishing-url', 'hide-phishing-link', 'url-phishing'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)