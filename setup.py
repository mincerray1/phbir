# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in phbir/__init__.py
from phbir import __version__ as version

setup(
	name='phbir',
	version=version,
	description='This app is for Philippine-specific features.',
	author='SERVIO Technologies',
	author_email='mmacutay@servio.ph',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
