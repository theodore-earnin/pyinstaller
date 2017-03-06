#-----------------------------------------------------------------------------
# Copyright (c) 2005-2017, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License with exception
# for distributing bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

import pytest
from PyInstaller.utils import misc

def test_save_py_data_struct(tmpdir):
    data = {'aa': b'\xe4\xf6\xfc',
            '42': (67, u'\xe4\xf6\xfc')}
    fn = str(tmpdir.join('aaa', 'out.dat'))
    misc.save_py_data_struct(fn, data)
    d = misc.load_py_data_struct(fn)
    assert d == data
