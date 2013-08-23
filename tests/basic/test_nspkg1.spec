# -*- mode: python -*-
#-----------------------------------------------------------------------------
# Copyright (c) 2013, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License with exception
# for distributing bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

# Since this .pth-file does not reside on a site-dir, we need to add
# it manually
import site
import os
site.addpackage(os.path.abspath(SPECPATH), 'nspkg1-nspkg.pth', None)

import sys ; logger.info(sys.modules['nspkg1'])

__testname__ = 'test_nspkg1'

a = Analysis([__testname__ + '.py'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name= __testname__ + '.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name= __testname__)
