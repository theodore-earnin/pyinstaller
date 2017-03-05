from __future__ import absolute_import

import os
import imp
import sys
import re
import marshal
import warnings
from codecs import lookup, BOM_UTF8

try:
    unicode
except NameError:
    unicode = str


if sys.version_info[0] == 2:
    from StringIO import StringIO as BytesIO
    from StringIO import StringIO

else:
    from io import BytesIO, StringIO



def imp_find_module(name, path=None):
    """
    same as imp.find_module, but handles dotted names
    """
    names = name.split('.')
    if path is not None:
        if isinstance(path, (str, unicode)):
            path = [os.path.realpath(path)]
    for name in names:
        result = imp.find_module(name, path)
        if result[0] is not None:
            result[0].close()
        path = [result[1]]
    return result

def _check_importer_for_path(name, path_item):
    try:
        importer = sys.path_importer_cache[path_item]
    except KeyError:
        for path_hook in sys.path_hooks:
            try:
                importer = path_hook(path_item)
                break
            except ImportError:
                pass
        else:
            importer = None
        sys.path_importer_cache.setdefault(path_item, importer)


    if importer is None:
        try:
            return imp.find_module(name, [path_item])
        except ImportError:
            return None
    return importer.find_module(name)

def imp_walk(name):
    """
    yields namepart, tuple_or_importer for each path item

    raise ImportError if a name can not be found.
    """
    warnings.warn("imp_walk will be removed in a future version", DeprecationWarning)

    if name in sys.builtin_module_names:
        yield name, (None, None, ("", "", imp.C_BUILTIN))
        return
    paths = sys.path
    res = None
    for namepart in name.split('.'):
        for path_item in paths:
            res = _check_importer_for_path(namepart, path_item)
            if hasattr(res, 'load_module'):
                if res.path.endswith('.py') or res.path.endswith('.pyw'):
                    fp = StringIO(res.get_source(namepart))
                    res = (fp, res.path, ('.py', 'rU', imp.PY_SOURCE))
                elif res.path.endswith('.pyc') or res.path.endswith('.pyo'):
                    co  = res.get_code(namepart)
                    fp = BytesIO(imp.get_magic() + b'\0\0\0\0' + marshal.dumps(co))
                    res = (fp, res.path, ('.pyc', 'rb', imp.PY_COMPILED))

                else:
                    res = (None, loader.path, (os.path.splitext(loader.path)[-1], 'rb', imp.C_EXTENSION))

                break
            elif isinstance(res, tuple):
                break
        else:
            break

        yield namepart, res
        paths = [os.path.join(path_item, namepart)]
    else:
        return

    raise ImportError('No module named %s' % (name,))



if sys.version_info[0] == 2:
    default_encoding = 'ascii'
    _re_flags = 0
else:
    default_encoding = 'utf-8'
    _re_flags = re.ASCII


_cookie_re = re.compile(r'^[ \t\f]*#.*coding[:=][ \t]*([-\w.]+)', _re_flags)
_blank_re = re.compile(br'^[ \t\f]*(?:[#\r\n]|$)', _re_flags)


# NOTE: This implementation will be replaced below by tokenize.detect_encoding if
# the later exists.
def _detect_encoding(readline):
    """
    Detect the encoding that should be used to decode a Python source file.
    """
    # This is basically a copy from Python 3.4 standard library tokenize.py.
    # Change are
    #  a) Default encoding is ascii for Python 2 (see above),
    #  b) _get_normal_name() has been put in here, and
    #  c) only return the encoding, not the lines.
    try:
        filename = readline.__self__.name
    except AttributeError:
        filename = None
    bom_found = False
    encoding = None
    default = default_encoding
    def read_or_stop():
        try:
            return readline()
        except StopIteration:
            return b''

    def _get_normal_name(orig_enc):
        """Imitates get_normal_name in tokenizer.c."""
        # Only care about the first 12 characters.
        enc = orig_enc[:12].lower().replace("_", "-")
        if enc == "utf-8" or enc.startswith("utf-8-"):
            return "utf-8"
        if enc in ("latin-1", "iso-8859-1", "iso-latin-1") or \
           enc.startswith(("latin-1-", "iso-8859-1-", "iso-latin-1-")):
            return "iso-8859-1"
        return orig_enc

    def find_cookie(line):
        try:
            # Decode as UTF-8. Either the line is an encoding declaration,
            # in which case it should be pure ASCII, or it must be UTF-8
            # per default encoding.
            line_string = line.decode('utf-8')
        except UnicodeDecodeError:
            msg = "invalid or missing encoding declaration"
            if filename is not None:
                msg = '{} for {!r}'.format(msg, filename)
            raise SyntaxError(msg)

        match = _cookie_re.match(line_string)
        if not match:
            return None
        encoding = _get_normal_name(match.group(1))
        try:
            codec = lookup(encoding)
        except LookupError:
            # This behaviour mimics the Python interpreter
            if filename is None:
                msg = "unknown encoding: " + encoding
            else:
                msg = "unknown encoding for {!r}: {}".format(filename,
                        encoding)
            raise SyntaxError(msg)

        if bom_found:
            if encoding != 'utf-8':
                # This behaviour mimics the Python interpreter
                if filename is None:
                    msg = 'encoding problem: utf-8'
                else:
                    msg = 'encoding problem for {!r}: utf-8'.format(filename)
                raise SyntaxError(msg)
            encoding += '-sig'
        return encoding

    first = read_or_stop()
    if first.startswith(BOM_UTF8):
        bom_found = True
        first = first[3:]
        default = 'utf-8-sig'
    if not first:
        return default

    encoding = find_cookie(first)
    if encoding:
        return encoding
    if not _blank_re.match(first):
        return default

    second = read_or_stop()
    if not second:
        return default

    encoding = find_cookie(second)
    if encoding:
        return encoding

    return default


try:
    # tokenize.detect_encoding() is new in Python 3.0
    from tokenize import detect_encoding as _detect_encoding

    def guess_encoding(fp):
        return _detect_encoding(fp.readline)[0] # return only the encoding

except ImportError:
    def guess_encoding(fp):
        # using our implementation above
        return _detect_encoding(fp.readline)
