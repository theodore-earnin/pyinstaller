#!/usr/bin/env python
#
# This file is part of the package for testing namespace eggs in
# `PyInstaller`.
#
# Author:    Hartmut Goebel <h.goebel@goebel-consult.de>
# Copyright: 2012 by Hartmut Goebel
# Licence:   GNU Public Licence v3 (GPLv3)
#

import sys, os
for i in (1, 2, 3):
    sys.path.append(os.path.join(os.path.dirname(__file__),
                                 'pyi_namespace_test.pkg%i.egg' % i))

import pyi_namespace_test.pkg3 as pkg3
assert pkg3.__name__ == 'pyi_namespace_test.pkg3'

import pyi_namespace_test.pkg2 as pkg2
assert pkg2.__name__ == 'pyi_namespace_test.pkg2'

import pyi_namespace_test.pkg1 as pkg1
assert pkg1.__name__ == 'pyi_namespace_test.pkg1'
