import os
from distutils.core import Extension, setup



setup(
    name="fcdimen",
    version="0.2.4",
    description="Python tools for analyzing dimensionality of materials structure using force constants.",
    long_description="Visit https://github.com/FCDimen/FCDimen",
    author="Mohammad Bagheri, Ethan Berger, Hannu-Pekka Komsa",
    author_email="Mohammad.Bagheri@oulu.fi",
    url="https://github.com/FCDimen/",
    install_requires=["numpy","phonopy", "ase", "networkx"],
    packages=[
        "fcdimen",
        "fcdimen.functions",
    ],
    scripts=[
        "scripts/fcdimen",
    ],
    classifiers=[
          "License :: OSI Approved :: BSD License",
          "Intended Audience :: Science/Research",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
          "Programming Language :: Python :: 3.10",
          "Programming Language :: Python :: 3.11",
          "Topic :: Scientific/Engineering :: Physics",
          "Topic :: Scientific/Engineering :: Chemistry"
          ],
)
