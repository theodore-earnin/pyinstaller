import unittest
import encodings
import encodings.aliases
from PyInstaller.lib.modulegraph import util
import sys
import os
from codecs import BOM_UTF8
import tempfile

try:
    from io import BytesIO
except ImportError:
    from cStringIO import StringIO as BytesIO

class TestUtil (unittest.TestCase):
    def assertStartsWith(self, a, b, message=None):
        if not a.startswith(b):
            if message is None:
                message = "%r does not start with %r"%(a, b)
            self.fail(message)

    def assertSamePath(self, a, b):
        self.assertStartsWith(os.path.realpath(a), os.path.realpath(b))

    def test_imp_find_module(self):
        fn = util.imp_find_module('encodings.aliases')[1]
        self.assertSamePath(encodings.aliases.__file__, fn)

    def test_imp_walk(self):
        imps = list(util.imp_walk('encodings.aliases'))
        self.assertEqual(len(imps), 2)

        self.assertEqual(imps[0][0], 'encodings')
        self.assertSamePath(encodings.__file__, imps[0][1][1])

        self.assertEqual(imps[1][0], 'aliases')
        self.assertSamePath(encodings.aliases.__file__, imps[1][1][1])

        # Close all files, avoid warning by unittest
        for i in imps:
            if i[1][0] is not None:
                i[1][0].close()


    def test_guess_encoding(self):
        fp = BytesIO(b"# coding: utf-8")
        self.assertEqual(util.guess_encoding(fp), "utf-8")

        fp = BytesIO(b"\n# coding: utf-8")
        self.assertEqual(util.guess_encoding(fp), "utf-8")

        fp = BytesIO(b"# coding: iso-8859-1")
        self.assertEqual(util.guess_encoding(fp), "iso-8859-1")

        # file starts with BOM
        fp = BytesIO(BOM_UTF8 + b"# coding: utf-8")
        self.assertEqual(util.guess_encoding(fp), "utf-8-sig")

        fp = BytesIO(b"\n# coding: latin-1")
        self.assertEqual(util.guess_encoding(fp), "iso-8859-1")

        fp = BytesIO(b"#!/usr/bin/env/python\n# vim: set fileencoding=latin-1 :")
        self.assertEqual(util.guess_encoding(fp), "iso-8859-1")

        fp = BytesIO(b"\n\n\n# coding: latin-1")
        if sys.version_info[0] == 2:
            self.assertEqual(util.guess_encoding(fp), "ascii")
        else:
            self.assertEqual(util.guess_encoding(fp), "utf-8")

        del fp

    def test_guess_encoding(self):
        # The actuall detection of the encoding is tested above, here only
        # test if file pointers are set to start of the file

        def make_tempfile(data):
            fd, name = tempfile.mkstemp()
            fp = os.fdopen(fd, 'wb')
            fp.write(data)
            fp.close()
            return name

        name = make_tempfile(b"\n# coding: utf-8")
        fp = util.open_source_text_file(name)
        self.assertEqual(fp.encoding, "utf-8")
        self.assertEqual(fp.tell(), 0)
        self.assertEqual(fp.read(), "\n# coding: utf-8")
        fp.close()
        os.unlink(name)

        name = make_tempfile(b"# coding: iso-8859-1")
        fp = util.open_source_text_file(name)
        self.assertEqual(fp.encoding, "iso-8859-1")
        self.assertEqual(fp.tell(), 0)
        self.assertEqual(fp.read(), "# coding: iso-8859-1")
        fp.close()
        os.unlink(name)

        # special case: file starts with BOM
        name = make_tempfile(BOM_UTF8 + b"# coding: utf-8")
        fp = util.open_source_text_file(name)
        self.assertEqual(fp.encoding, "utf-8-sig")
        self.assertEqual(fp.tell(), 0)
        self.assertEqual(fp.read(), "# coding: utf-8")
        fp.close()
        os.unlink(name)

        name = make_tempfile(b"\n\n\n# coding: latin-1")
        fp = util.open_source_text_file(name)
        if sys.version_info[0] == 2:
            self.assertEqual(fp.encoding, "ascii")
        else:
            self.assertEqual(fp.encoding, "utf-8")
        self.assertEqual(fp.tell(), 0)
        self.assertEqual(fp.read(), "\n\n\n# coding: latin-1")
        fp.close()
        os.unlink(name)


if __name__ == "__main__":
    unittest.main()
