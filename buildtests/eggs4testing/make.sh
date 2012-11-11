#!/bin/sh
#
# This file is part of the package for testing eggs in `PyInstaller`.
#
# Author:    Hartmut Goebel <h.goebel@goebel-consult.de>
# Copyright: 2012 by Hartmut Goebel
# Licence:   GNU Public Licence v3 (GPLv3)
#

cd "$(dirname "$0")"

# the eggs should not contain bytecode to be version independant
export PYTHONDONTWRITEBYTECODE=1

rm -rf build/ dist/ *.egg-info

for pkg_name in zipped unzipped \
                namespace-pkg1 namespace-pkg2 namespace-pkg3 ; do
    python setup-${pkg_name}.py bdist_egg
    # need to clean up build-dir after each build, otherwise stuff
    # from the last build goes into the next one.
    rm -rf build/ *.egg-info
done

unset PYTHONDONTWRITEBYTECODE

# setup a virtualenv for testing
virtualenv venv --distribute
. venv/bin/activate
easy_install --zip-ok dist/zipped_egg*.egg
easy_install --always-unzip dist/unzipped_egg*.egg
easy_install --zip-ok dist/pyi_namespace_test.pkg*.egg
cp ../import/test_eggs*.py venv
cp ../import/test_namespace*.py venv

# see if the unpackaged test-case still works
cd venv
python test_eggs1.py || exit 2
python test_eggs2.py || exit 2
python test_namespace1.py || exit 2
cd ..

cd venv
rm -rfv ../../import/zipped.egg ../../import/unzipped.egg
mv -v lib/python*.*/site-packages/zipped_egg-*.egg ../../import/zipped.egg
mv -v lib/python*.*/site-packages/unzipped_egg-*.egg ../../import/unzipped.egg

for pkg_name in pkg1 pkg2 pkg3 ; do
    pkg_name=pyi_namespace_test.${pkg_name}
    mv -v lib/python*.*/site-packages/${pkg_name}-*.egg ../../import/${pkg_name}.egg
done

cd ..

deactivate

rm -rf build/ dist/ venv *.egg-info
