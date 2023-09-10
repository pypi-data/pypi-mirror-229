import os
from setuptools import setup

# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "burpr3",
    version = "0.0.1",
    author = "Krystian Bajno",
    author_email = "krystian.bajno@gmail.com",
    description = ("A Burp Suite request parser, used for aid in assessing application security functionality."),
    license = "MIT",
    long_description_content_type='text/markdown',
    keywords = "burp suite burpsuite request parser",
    url = "https://github.com/krystianbajno/burpr",
    packages=['burpr', 'burpr.enums', 'burpr.models'],
    install_requires=["urllib3"],
    long_description=read('README.md'),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)