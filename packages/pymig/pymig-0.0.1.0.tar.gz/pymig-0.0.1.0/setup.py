#!/usr/bin/env python
# -*- encoding: utf8 -*-
# import glob
# import inspect
# import io
# import os

from setuptools import setup
from distutils.core import Extension
import numpy


long_description = """
Source code: https://github.com/chenyk1990/pymig""".strip() 


def read(*names, **kwargs):
    return io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")).read()

from distutils.core import Extension

srcs=[
'pymig/src/mig_alloc.c',
]

										
nprec3d_module = Extension('npre3dcfun', sources=srcs+['pymig/src/npre3d.c'],include_dirs=[numpy.get_include()])

# Note updated yet
warp_module = Extension('warpcfun', sources=srcs+['pymig/src/warp.c'], include_dirs=[numpy.get_include()])	
# from numpy.distutils.core import setup 
setup(
    name="pymig",
    version="0.0.1.0",
    license='GNU General Public License, Version 3 (GPLv3)',
    description="A python package for seismic data processing and inversion",
    long_description=long_description,
    author="pymig developing team",
    author_email="chenyk2016@gmail.com",
    url="https://github.com/chenyk1990/pymig",
    ext_modules=[nprec3d_module],
    packages=['pymig'],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list:
        # http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ],
    keywords=[
        "seismology", "earthquake seismology", "exploration seismology", "array seismology", "denoising", "science", "engineering", "structure", "local slope", "filtering"
    ],
    install_requires=[
        "numpy", "scipy", "matplotlib"
    ],
    extras_require={
        "docs": ["sphinx", "ipython", "runipy"]
    }
)
