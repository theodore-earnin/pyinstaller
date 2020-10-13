# Debian-based container for running PyInstaller builds/tests
#
# This serves primarily to make it easier for e.g. macOS-based
# developers to run the tests in a Linux environment *before*
# opening a pull request. See test-docker.sh for usage.
#
# Note: this functionality is contributed and not maintained
# by the PyInstaller maintainers. If you find it useful,
# please consider contributing to its maintenance and improvement.

FROM python:3.7

RUN mkdir /src

COPY requirements.txt /src
COPY tests/requirements-developer.txt src/tests/requirements-developer.txt
COPY tests/requirements-tools.txt src/tests/requirements-tools.txt
COPY tests/requirements-libraries.txt src/tests/requirements-libraries.txt
RUN pip install -r src/requirements.txt
RUN pip install -r src/tests/requirements-tools.txt
RUN pip install -r src/tests/requirements-libraries.txt

ADD *.py setup.cfg README.rst MANIFEST.in .pylintrc /src/
ADD PyInstaller /src/PyInstaller
ADD bootloader /src/bootloader
ADD doc /src/doc

RUN rm -rf /src/PyInstaller/bootloader/*

WORKDIR /src/bootloader
RUN python waf distclean all

WORKDIR /src
RUN python setup.py install

ADD tests /src/tests
