"""Setuptools script for pip package."""
import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name="boincrpc",
    version="0.1.4.dev1",
    author="Yevhen Shyshkan",
    author_email="eugene.tx200@gmail.com",
    #license="LGPLv3+",
    description="Python implementation of the BOINC GUI RPC protocol",
    long_description=long_description,
    long_description_content_type="text/markdown",
    #url="",
    #packages=setuptools.find_packages(),
    py_modules=['boincrpc'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
    ],
    python_requires='>=3.6',
)
