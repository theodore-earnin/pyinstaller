#!/usr/bin/env python
#
# This file is part of the package for testing eggs in `PyInstaller`.
#
# Author:    Hartmut Goebel <h.goebel@goebel-consult.de>
# Copyright: 2012 by Hartmut Goebel
# Licence:   GNU Public Licence v3 (GPLv3)
#

from setuptools import setup

pgk_name = 'pyi_namespace_test.pkg3'
setup(name=pgk_name,
      version='0.1',
      description='An egg for testing namespaces with PyInstaller',
      packages=['pyi_namespace_test', pgk_name],
      namespace_packages=['pyi_namespace_test'],
     )
