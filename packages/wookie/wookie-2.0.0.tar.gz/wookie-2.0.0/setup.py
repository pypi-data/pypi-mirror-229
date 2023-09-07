from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
	name="wookie",

	version="2.0.0",

	author="Nexachromic",

	author_email="nexachromic@gmail.com",

	license="MIT",

	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
