#! /usr/bin/env python

from setuptools import Command, Extension, setup
from setuptools.command.build_ext import build_ext


DISTNAME = "new-pkgsetup"
DESCRIPTION = "test project using setuptools"

if __name__ == "__main__":
    setup()
 
#mk  works 9/3

import newpkg

#import newpkg as somethingelse


# example below is from scikit setup.py

# We can actually import a restricted version of sklearn that
# does not need the compiled code
#import sklearn  # noqa
#import sklearn._min_dependencies as min_deps  # noqa
#from sklearn._build_utils import _check_cython_version  # noqa
#from sklearn.externals._packaging.version import parse as parse_version  # noqa
