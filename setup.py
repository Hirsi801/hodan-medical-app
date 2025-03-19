from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in medical_app/__init__.py
from medical_app import __version__ as version

setup(
	name="medical_app",
	version=version,
	description="medical app",
	author="rasiin",
	author_email="rasiin@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
