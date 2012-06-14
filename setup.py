#!/usr/bin/env python

import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "geweb",
    version = "0.0.4",
    author = "Artem Sazhin",
    author_email = "arts@posint.im",
    description = ("Asyncronous python/gevent web framework."),
    license = "BSD",
    keywords = "web framework gevent",
    url = "http://bitbucket.org/arts/geweb",
    packages=["geweb", "geweb.template", "geweb.session", "geweb.util"],
    long_description=read("README.md"),
    install_requires=["gevent", "jinja2"],
    scripts=["geweb/bin/geweb.py"],

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: BSD License",
    ],
)
