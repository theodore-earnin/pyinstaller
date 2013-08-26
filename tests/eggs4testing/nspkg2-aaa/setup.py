

from setuptools import setup, find_packages

setup(
    name='nspkg2-aaa',
    version='0.1',
    description='A test package for name-spaces',
    zip_safe=False,
    packages=find_packages(),
    namespace_packages = ['nspkg2']
    )
