#-----------------------------------------------------------------------------
# Copyright (c) 2013, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License with exception
# for distributing bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

# If both distutils and sysconfig are imported, pyconfig.h must still
# only be in the archive once. Otherwise the loader will fail with
# "file already exists but should not".
#
# Unfortunatly this error does not occur on multiarch plattforms.
#

import distutils.sysconfig
import sysconfig


config_h = sysconfig.get_config_h_filename()
print('sysconfig pyconfig.h: ' + config_h)
files = [config_h]

config_h = distutils.sysconfig.get_config_h_filename()
print('distutils pyconfig.h: ' + config_h)
files.append(config_h)

for f in files:
    if not os.path.exists(f):
        raise SystemExit('File does not exist: %s' % f)
print 'okay'
