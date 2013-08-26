#-----------------------------------------------------------------------------
# Copyright (c) 2013, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License with exception
# for distributing bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------


# This file is part of the package for testing eggs in `PyInstaller`.


export PYTHONDONTWRITEBYTECODE=1

rm -rf build/ dist/ *.egg* */*.egg* */build/ */dist/

python setup-zipped.py bdist_egg
# nedd to clean up build-dir, otherwise stuff from `zipped_egg`
# goes into `unzipped_egg*.egg`
rm -rf build/
python setup-unzipped.py bdist_egg
rm -rf build/

PKGS="nspkg2-aaa nspkg2-bbb nspkg2-ccc"

distdir="$PWD"/dist

for pkg in $PKGS ; do
    cd $pkg
    python setup.py sdist --dist-dir "$distdir"
    python setup.py bdist_egg --dist-dir "$distdir"
    cd -
done

# setup a virtualenv for testing
virtualenv venv --distribute
. venv/bin/activate
easy_install --zip-ok "$distdir"/zipped_egg*.egg
easy_install --always-unzip "$distdir"/dist/unzipped_egg*.egg
easy_install "$distdir"/nspkg2_*.egg
cp ../import/test_{eggs,nspkg2}*.py venv

# see if the unpackaged test-case still works
cd venv
python test_eggs1.py
python test_eggs2.py
python test_nspkg2.py
cd ..

cd venv
rm -rfv ../../import/zipped.egg ../../import/unzipped.egg
mv -v lib/python2.7/site-packages/zipped_egg-*.egg ../../import/zipped.egg
mv -v lib/python2.7/site-packages/unzipped_egg-*.egg ../../import/unzipped.egg
mv -v lib/python2.7/site-packages/nspkg2_aaa-*.egg/ ../../import/nspkg2_aaa.egg
mv -v lib/python2.7/site-packages/nspkg2_bbb-*.egg/ ../../import/nspkg2_bbb.egg
mv -v lib/python2.7/site-packages/nspkg2_ccc-*.egg/ ../../import/nspkg2_ccc.egg
cd ..

deactivate

rm -rf build/ dist/ *.egg* */*.egg* */build/ */dist/ venv
