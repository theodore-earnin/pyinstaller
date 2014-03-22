#-----------------------------------------------------------------------------
# Copyright (c) 2013, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License with exception
# for distributing bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------


"""
Viewer for archives packaged by archive.py
"""


import optparse
import os
import re
import inspect

import PyInstaller.build
from PyInstaller.utils import misc

PATTERN = re.compile(r"^out\d+-(.*).toc$")

class TOCFilenameError(Exception): pass


def _c_Analysis(guts, what_requires=None, **kw):
    import pprint ; pprint.pprint(guts)
    if what_requires:
        print guts['pure'][0]


def main(toc_filename, opts):
    misc.check_not_running_as_root()

    try:
        toc_type = PATTERN.match(os.path.basename(toc_filename)).group(1)
    except:
        raise TOCFilenameError('Filename does not match required pattern.')

    try:
        toc_class = getattr(PyInstaller.build, toc_type)
        assert issubclass(toc_class, PyInstaller.build.Target)
    except:
        raise TOCFilenameError("'%s' is not a valid TOC type." % toc_type)

    guts = PyInstaller.build._load_data(toc_filename)
    guts = dict(zip([g[0] for g in toc_class.GUTS], guts))
    import pprint ; pprint.pprint(guts)
    return
    try:
        func = getattr(inspect.getmodule(main), '_c_' + toc_type)
    except:
        raise TOCFilenameError('Searching this type of .toc-file is not '
                               'yet implemented. Sorry.')
    func(guts, **opts)


def run():
    parser = optparse.OptionParser('%prog [options] toc-file')
    parser.add_option('--what-requires', nargs=1)

    opts, args = parser.parse_args()
    if len(args) != 1:
        parser.error('Requires exactly one pyinstaller .toc file-name')

    try:
        raise SystemExit(main(args[0], vars(opts)))
    except TOCFilenameError, e:
        raise SystemExit(str(e))
    except KeyboardInterrupt:
        raise SystemExit("Aborted by user request.")
