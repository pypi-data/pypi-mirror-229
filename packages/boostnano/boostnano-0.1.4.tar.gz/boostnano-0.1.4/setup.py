from setuptools import find_packages
from distutils.core import setup, Extension
import sys
import numpy as np
from Cython.Build import cythonize

ext_modules = [ Extension('boostnano.hmm', sources = ['boostnano/hmm.cpp'],language='c++',include_dirs=['boostnano'])]
ext_modules = cythonize(ext_modules,force = True, language_level = 3)
exec(open('boostnano/_version.py').read()) #readount the __version__ variable
setup(
	name = 'boostnano',
	version = __version__,
	include_dirs = [np.get_include(),'boostnano'],
	ext_modules = ext_modules,
	packages=find_packages(),
    package_data={
        'boostnano': ['boostnano/model/*'],  # Include all files under the 'data' directory
    },
    include_package_data=True,
)
