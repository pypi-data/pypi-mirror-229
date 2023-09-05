import setuptools
import glob

import os
from setuptools import Extension, setup, find_packages
from setuptools.command.build_ext import build_ext
from pathlib import Path


libName="MAZAlib"

with open("README.md", "r") as fh:
    long_description = fh.read()

imaza_module = Extension(libName, sources=['./src/imaza/imaza.cpp'],
			language="c++", 
			extra_compile_args=["-std=c++17",'-O3', '-w'],
			extra_link_args=["-std=c++17"],
			include_dirs=['./src/mydist/'],
			# libraries = ["mydist"],
			library_dirs = ["./src/mydist/"],
            extra_objects=["./src/mydist/libmydist.a"]
			)

setup(
    name=libName,
    version="0.0.25",
    description='TODO',
    long_description=long_description,
    author='Mathieu Gravey, Roman V. Vasilyev, Timofey Sizonenko, Kirill M. Gerke, Marina V. Karsanina',
    author_email='mathieu.gravey@unil.ch',
    license='GPLv3',
    packages=find_packages('src',include=['imaza*'])+['mydist'],
    package_dir={'': 'src'},
    package_data={'mydist': ['./libmydist.a', './mydist.h']},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: C++',
        'Programming Language :: Python :: 3 :: Only',
        'Operating System :: OS Independent'
    ],
    ext_modules=[imaza_module]
    # ext_modules=[CMakeExtension('imaza')],
    # cmdclass={'build_ext': CMakeBuild}
)