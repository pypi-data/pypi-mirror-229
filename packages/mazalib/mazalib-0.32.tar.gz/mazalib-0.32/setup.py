#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import glob
from sys import argv
import numpy as np
isST=True
from setuptools import setup, Extension, find_packages
from os import listdir
from os.path import isfile, join
import platform
systemName=platform.system()
import sys
is_64bits = sys.maxsize > 2**32


version='0.32'
libName="mazalib"

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            p = os.path.join("./", path, filename)
            paths.append("/".join(p.split("/")[4:]))
    return paths

with open("README.md", "r") as fh:
	long_description = fh.read()
short_description = "Cross-platform 2d/3d image segmentation C++ library"

mazalib_module = Extension(libName, sources=['./src/mazalib/mazalib.cpp'],
			language="c++", 
			extra_compile_args=["-std=c++17",'-O3', '-w'],
			extra_link_args=["-std=c++17"],
			include_dirs=["./src/segmentation/include/", "./src/non_local_means/include/", "./src/eigen3/"],
			library_dirs = ["./src/segmentation/", "./src/non_local_means/"],
            extra_objects=["./src/segmentation/libsegmentation.a", "./src/non_local_means/libnon_local_means.a"]
			)

extraFlags=['-fpermissive','-std=c++17']

installRequiresList=['numpy','matplotlib','tk','Pillow','imageio']

entry_points_Command={"gui_scripts": [ libName+" = "+libName+"."+libName+"_gui:main"]}


if(systemName=='Darwin' or systemName=='Linux'):

	os.environ["CXX"]='g++'
	os.environ["CC"]='gcc'
	setup(
		name=libName,
		version=version,
		description=short_description,
		long_description=long_description,
		author='Mathieu Gravey, Roman V. Vasilyev, Timofey Sizonenko, Kirill M. Gerke, Marina V. Karsanina',
		author_email='mathieu.gravey@unil.ch',
		license='GPLv3',
		packages=find_packages('src',include=['mazalib*'])+['non_local_means', 'segmentation', 'eigen3'],
    	package_dir={'': 'src'},
    	package_data={'non_local_means': ['./libnon_local_means.a', './include/*.h'],
				      'segmentation': ['./libsegmentation.a', './include/*.h'],
					  'eigen3': package_files("./src/eigen3/")},
		classifiers=[
			'Development Status :: 3 - Alpha',
			'Intended Audience :: Science/Research',
			'Intended Audience :: Education',
			'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
			'Programming Language :: C++',
			'Programming Language :: Python :: 3 :: Only',
			'Operating System :: OS Independent'
		],
		# ext_package = libName,
		ext_modules=[mazalib_module],
		install_requires=installRequiresList,
		entry_points=entry_points_Command
	)

# if(systemName=='Windows'):
# 	import numpy
# 	if is_64bits:
# 		setup(name=libName,
# 			version=version,
# 			description=short_description,
# 			long_description=long_description,
# 			author='Mathieu Gravey, Roman V. Vasilyev, Timofey Sizonenko, Kirill M. Gerke, Marina V. Karsanina',
# 			author_email='mathieu.gravey@unil.ch',
# 			license='GPLv3',
# 			packages=[libName],
# 			classifiers=[
# 				'Development Status :: 3 - Alpha',
# 				'Intended Audience :: Science/Research',
# 				'Intended Audience :: Education',
# 				#'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
# 				'Programming Language :: C++',
# 				'Programming Language :: Python :: 3 :: Only'
# 			],
# 			ext_package = libName,
# 			ext_modules=[Extension(libName, sources=['./pythonInterface.cpp']+glob.glob('../non_local_means/src/*.cpp')+glob.glob('../lib/*.cpp'),
# 			language="c++", 
# 			extra_compile_args=["-std=c++14",'-O3']+extraFlags,
# 			extra_link_args=["-std=c++14"]+extraFlags,
# 			include_dirs=['../lib','../non_local_means/include','../eigen3'],
# 			libraries = [],
# 			library_dirs = []
# 			)],
# 			include_dirs=numpy.get_include(),
# 			install_requires=installRequiresList,
# 			entry_points=entry_points_Command
# 			#data_files=[('lib\\site-packages\\g2s',["./libzmq-v141-x64-4_3_2/libzmq-v141-mt-4_3_2.dll","./libzmq-v141-x64-4_3_2/libsodium.dll"])]
# 		)
# 	else:
# 		setup(name=libName,
# 			version=version,
# 			description='TBA',
# 			long_description=long_description,
# 			**{'long_description_content_type':'text/markdown'} if isST else {},
# 			author='Mathieu Gravey, Roman V. Vasilyev, Timofey Sizonenko, Kirill M. Gerke, Marina V. Karsanina',
# 			author_email='mathieu.gravey@unil.ch',
# 			url='TBA',
# 			license='TBA',
# 			packages=[libName],
# 			classifiers=[
# 				'Development Status :: 3 - Alpha',
# 				'Intended Audience :: Science/Research',
# 				'Intended Audience :: Education',
# 				#'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
# 				'Programming Language :: C++',
# 				'Programming Language :: Python :: 3 :: Only'
# 			],
# 			ext_package = libName,
# 			ext_modules=[Extension(libName, sources=['./pythonInterface.cpp']+glob.glob('../non_local_means/src/*.cpp')+glob.glob('../lib/*.cpp'),
# 			language="c++", 
# 			extra_compile_args=["-std=c++14",'-O3']+extraFlags,
# 			extra_link_args=["-std=c++14"]+extraFlags,
# 			include_dirs=['../lib','../non_local_means/include','../eigen3'],
# 			libraries = [],
# 			library_dirs = []
# 			)],
# 			include_dirs=numpy.get_include(),
# 			install_requires=installRequiresList,
# 			entry_points=entry_points_Command
# 			#data_files=[('lib\\site-packages\\g2s',["./libzmq-v141-4_3_2/libzmq-v141-mt-4_3_2.dll","./libzmq-v141-4_3_2/libsodium.dll"])]
# 		)