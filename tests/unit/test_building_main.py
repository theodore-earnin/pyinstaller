#-----------------------------------------------------------------------------
# Copyright (c) 2005-2017, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License with exception
# for distributing bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------


import pytest
import os
from codecs import BOM_UTF8

from PyInstaller.building import build_main
from PyInstaller.utils.tests import skipif, is_py3


class TestPythonEncoding:

    EXPECTED_ERROR = SyntaxError

    @staticmethod
    def comp(contents, tmpdir):
        __tracebackhide__ = True
        return compile(contents, '<string>', 'exec')

    def test_encoding(self, tmpdir):
        def comp(contents):
            __tracebackhide__ = True
            self.comp(contents, tmpdir)

        # default encoding
        if not is_py3:
            # default encoding is ascii
            comp(b"print( '\xe4\xf6\xfc')")
            comp(b"print(u'\xe4\xf6\xfc')")
        else:
            # default encoding is utf-8
            comp(b"print( '\xc3\xa4\xc3\xb6\xc3\xbc')")
            comp(b"print(u'\xc3\xa4\xc3\xb6\xc3\xbc')")

        # specified encoding: valid latin-1
        comp(b"# coding: latin-1\nprint( '\xe4\xf6\xfc')")
        comp(b"# coding: latin-1\nprint(u'\xe4\xf6\xfc')")

        # specified encoding: valid utf-8
        comp(b"# coding: utf-8\nprint( '\xc3\xa4\xc3\xb6\xc3\xbc')")
        comp(b"# coding: utf-8\nprint(u'\xc3\xa4\xc3\xb6\xc3\xbc')")

        # specified encoding: valid utf-8, file starts with BOM
        comp(BOM_UTF8 + b"# coding: utf-8\nprint( '\xc3\xa4\xc3\xb6\xc3\xbc')")
        comp(BOM_UTF8 + b"# coding: utf-8\nprint(u'\xc3\xa4\xc3\xb6\xc3\xbc')")


    def test_invalid_encoding(self, tmpdir):
        def comp(contents):
            __tracebackhide__ = True
            self.comp(contents, tmpdir)

        # default encoding
        if not is_py3:
            # in Python 2, the literal is interpreted as byte-string, thus
            # decoding is not applied and this is valid code
            # unicode literal
            comp(b"print( '\xc3\xa4\xc3\xb6\xc3\xbc')")
            # unicode literal
            # FIXME: Explain why this passes
            comp(b"print(u'\xc3\xa4\xc3\xb6\xc3\xbc')")
        else:
            # non-unicode literal
            with pytest.raises(self.EXPECTED_ERROR) as excinfo:
                comp(b"print( '\xe4\xf6\xfc')")
            assert "'utf-8' codec can't decode byte" in str(excinfo.value)

            # unicode literal
            with pytest.raises(self.EXPECTED_ERROR) as excinfo:
                comp(b"print(u'\xe4\xf6\xfc')")
            assert "'utf-8' codec can't decode byte" in str(excinfo.value)

        # specified encoding: invalid utf-8
        # non-unicode literal
        if not is_py3:
            # in Python 2, the literal is interpreted as byte-string, thus
            # decoding is not applied and this is valid code
            comp(b"# coding: utf-8\nprint('\xe4\xf6\xfc')")
        else:
            with pytest.raises(self.EXPECTED_ERROR) as excinfo:
                comp(b"# coding: utf-8\nprint('\xe4\xf6\xfc')")
            assert "codec can't decode byte" in str(excinfo.value)
        # unicode literal
        with pytest.raises(self.EXPECTED_ERROR) as excinfo:
            comp(b"# coding: utf-8\nprint(u'\xe4\xf6\xfc')") # unicode literal
        assert "codec can't decode byte" in str(excinfo.value)

        # specified encoding: invalid ascii
        # non.unicode literal
        with pytest.raises(self.EXPECTED_ERROR) as excinfo:
            comp(b"# coding: ascii\nprint('\xe4\xf6\xfc')")
        assert "codec can't decode byte" in str(excinfo.value)
        # unicode literal
        with pytest.raises(self.EXPECTED_ERROR) as excinfo:
            comp(b"# coding: ascii\nprint(u'\xe4\xf6\xfc')")
        assert "codec can't decode byte" in str(excinfo.value)

    def test_encoding_in_comments(self, tmpdir):
        def comp(contents):
            __tracebackhide__ = True
            self.comp(contents, tmpdir)

        # default encoding
        if not is_py3:
            # default encoding is ascii
            comp(b"# \xe4\xf6\xfc")
        else:
            # default encoding is utf-8
            comp(b"# \xc3\xa4\xc3\xb6\xc3\xbc")

        # specified encoding:
        comp(b"# coding: latin-1\n# \xe4\xf6\xfc")
        comp(b"# coding: utf-8\n# \xc3\xa4\xc3\xb6\xc3\xbc")
        comp(BOM_UTF8 + b"# coding: utf-8\n# \xc3\xa4\xc3\xb6\xc3\xbc")


    def test_invalid_encoding_in_comments(self, tmpdir):
        def comp(contents):
            __tracebackhide__ = True
            self.comp(contents, tmpdir)

        # for 8-bit codecs, the content does not matter
        # default encoding, invalid data
        if not is_py3:
            comp(b"# \xc3\xa4\xc3\xb6\xc3\xbc")
        else:
            comp(b"# \xe4\xf6\xfc")
        # specified encoding: invalid utf-8
        comp(b"# coding: utf-8\n# \xe4\xf6\xfc")

        # specified encoding: invalid ascii
        # for 7-bit ascii, the content *does* matter
        with pytest.raises(self.EXPECTED_ERROR) as excinfo:
            comp(b"# coding: ascii\n# \xe4\xf6\xfc")
        assert "codec can't decode byte" in str(excinfo.value)


class TestSpecEncoding(TestPythonEncoding):

    # build_main catches compile errors and raises SystemExit instead
    EXPECTED_ERROR = SystemExit

    @staticmethod
    def comp(contents, tmpdir):
        __tracebackhide__ = True
        spec = tmpdir.join('test.spec')
        spec.write_binary(contents)
        build_main.build(str(spec), str(tmpdir), str(tmpdir), False)
