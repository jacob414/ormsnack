#!/usr/bin/env python
# yapf

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

install = (
    "funcy>=1.10.2",
    "pysistence>=0.4.1",
    "patterns>=0.3",
    "jsonpickle>=1.2",
    "astunparse>=1.6.3",
    "kingston>=0.6.7",
    'astor>=0.8.1',
)  # yapf: disable

develop = (
    "pytest>=5.0.1",
    "hypothesis>=4.24.3",
    "altered_states>=1.0.9",
    "pytest-cov>=2.7.1",
)  # yapf: disable

setup(
    name='ormsnack',
    version='0.0.1',
    description=next(line for line in open('README.org').readlines()
                     if line.startswith('* '))[2:],
    packages=('ormsnack', ),
    author='Jacob Oscarson',
    author_email='jacob@414soft.com',
    install_requires=install,
    extras_require={
        'test': install + develop,
    },
    license='MIT',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License (MIT)',
        'Operating System :: OS Independent',
    ],
)
