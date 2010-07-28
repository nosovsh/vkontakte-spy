import time
import re
import StringIO
from cookielib import CookieJar, _warn_unhandled_exception, LoadError, Cookie


class StringCookieJar(CookieJar):
    """A FileCookieJar that can load from and save cookies to string.
    
    For simplicity all code is taken from `MozillaCookieJar` class,
    so it is not very elegant and saved in Mozilla format.
    TODO: rewrite this class.
    """
    def __init__(self, cookiestring='', policy=None):
        CookieJar.__init__(self, policy)
        self.cookiestring = cookiestring
        if not cookiestring:
            return
        f = StringIO.StringIO(cookiestring)
        try:
            self._really_load(f, '[No file. Content loaded from string]', False, False)
        finally:
            f.close()

    magic_re = "#( Netscape)? HTTP Cookie File"
    header = """\
    # Netscape HTTP Cookie File
    # http://www.netscape.com/newsref/std/cookie_spec.html
    # This is a generated file!  Do not edit.

"""

    def _really_load(self, f, filename, ignore_discard, ignore_expires):
        """Parse cookies from string. Copied from MozillaCookieJar."""
        now = time.time()

        magic = f.readline()
        if not re.search(self.magic_re, magic):
            f.close()
            raise LoadError(
                "%r does not look like a Netscape format cookies file" %
                filename)

        try:
            while 1:
                line = f.readline()
                if line == "": break

                # last field may be absent, so keep any trailing tab
                if line.endswith("\n"): line = line[:-1]

                # skip comments and blank lines XXX what is $ for?
                if (line.strip().startswith(("#", "$")) or
                    line.strip() == ""):
                    continue
                domain, domain_specified, path, secure, expires, name, value = \
                        line.split("\t")
                secure = (secure == "TRUE")
                domain_specified = (domain_specified == "TRUE")
                if name == "":
                    # cookies.txt regards 'Set-Cookie: foo' as a cookie
                    # with no name, whereas cookielib regards it as a
                    # cookie with no value.
                    name = value
                    value = None

                initial_dot = domain.startswith(".")
                assert domain_specified == initial_dot

                discard = False
                if expires == "":
                    expires = None
                    discard = True

                # assume path_specified is false
                c = Cookie(0, name, value,
                           None, False,
                           domain, domain_specified, initial_dot,
                           path, False,
                           secure,
                           expires,
                           discard,
                           None,
                           None,
                           {})
                if not ignore_discard and c.discard:
                    continue
                if not ignore_expires and c.is_expired(now):
                    continue
                self.set_cookie(c)

        except IOError:
            raise
        except Exception:
            _warn_unhandled_exception()
            raise LoadError("invalid Netscape format cookies file %r: %r" %
                            (filename, line))

    def save(self, ignore_discard=False, ignore_expires=False):
        """Convert cookies to string and return it.

        Mostly copied from MozillaCookieJar.

        """
        f = StringIO.StringIO()
        try:
            f.write(self.header)
            now = time.time()
            for cookie in self:
                if not ignore_discard and cookie.discard:
                    continue
                if not ignore_expires and cookie.is_expired(now):
                    continue
                if cookie.secure: secure = "TRUE"
                else: secure = "FALSE"
                if cookie.domain.startswith("."): initial_dot = "TRUE"
                else: initial_dot = "FALSE"
                if cookie.expires is not None:
                    expires = str(cookie.expires)
                else:
                    expires = ""
                if cookie.value is None:
                    # cookies.txt regards 'Set-Cookie: foo' as a cookie
                    # with no name, whereas cookielib regards it as a
                    # cookie with no value.
                    name = ""
                    value = cookie.name
                else:
                    name = cookie.name
                    value = cookie.value
                f.write(
                    "\t".join([cookie.domain, initial_dot, cookie.path,
                               secure, expires, name, value])+
                    "\n")
        finally:
            ret = f.getvalue()
            f.close()
            return ret
