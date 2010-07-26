import logging
import urllib2
import urllib
import re
import os
import time
from pprint import pprint

from stringcookiejar import StringCookieJar


headers = {
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.0.'
        '13) Gecko/2009073022 Firefox/3.0.13 (.NET CLR 3.5.30729)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;'
        'q=0.8',
        'Accept-Language': 'ru,en-us;q=0.7,en;q=0.3',
        'Accept-Charset': 'windows-1251,utf-8;q=1,*;q=0',
        'Keep-Alive': '300',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded',
        }


class VKError(Exception):
    pass


class VKConnector:
    """Connector to vkontakte web site.

    Can get pages from vkontakte web site.
    Automatically log in if session is timed out.

    """
    def __init__(self, email=None, password=None, cookiestring=''):
        self.email = email
        self.password = password
        self.cookiejar = StringCookieJar(cookiestring)
        self.maxreloads = 2
        self.sleeptime = 2
        self.vkhost = 'http://vkontakte.ru'
        self.vkloginhost = 'http://login.vk.com'

        handler = urllib2.HTTPCookieProcessor(self.cookiejar)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)

    def get_page(self, path):
        """Get page from vkontakte web site.

        path -- absolute path to page with slash at the beginning.

        """
        for i in xrange(self.maxreloads):
            # sleep to not be banned
            time.sleep(self.sleeptime)
            data = None
            req = urllib2.Request(self.vkhost + path, data, headers)
            handle = urllib2.urlopen(req)
            text = handle.read()
            if len(text) < 1100:
                # session timed out
                self.relogin()
            else:
                text = text.decode('cp1251')
                return text
        raise VKError('Could not get page from %s. Please, try again later.',
                      self.vkhost)

    def relogin(self):
        """Refresh session. Email and password are not needed."""
        # 1.get s-value
        data = None
        req = urllib2.Request(self.vkloginhost + '/?vk=', data, headers)
        handle = urllib2.urlopen(req)
        text = handle.read()
        match = re.search(r"action='(.*?)'.*?name='s' id='s' value='(.*?)'",
                          text, re.DOTALL)
        if match:
            # action and svalue should be something like
            # "http://vk.com/login.php?op=slogin&nonenone=1"
            # and "nonenone"
            action, svalue = match.group(1), match.group(2)
        else:
            raise VKError("s-value not returned.")

        # 2.submitting s-value
        data = urllib.urlencode({'s': svalue})
        req = urllib2.Request(action, data, headers)
        handle = urllib2.urlopen(req)
        # text should be "<html></html>"
        text = handle.read()
        # if valid s-value not returned we should login again
        if svalue == 'nonenone':
            self.login()
        # else, remixsid cookie have been received and
        # any page can be accessed
        else:
            return

    def get_cookie(self):
        """Get cookie in text format.

        Can be saved and then passed to VKConnector constructor.

        """
        return self.cookiejar.save()

    def login(self):
        """Log in to vkontakte web site."""
        # 1.visit index page
        data = None
        req = urllib2.Request(self.vkhost + '/index.php', data, headers)
        handle = urllib2.urlopen(req)
        text = handle.read()

        # 2.get s-form from http://login.vk.com/?vk=1
        data = None
        req = urllib2.Request(self.vkloginhost + '/?vk=', data, headers)
        handle = urllib2.urlopen(req)
        text = handle.read()

        # 3.submit this form (send s-value)
        data = urllib.urlencode({'s': 'nonenone'})
        req = urllib2.Request(self.vkhost + '/login.php?op=slogin&nonenone=1',
                              data, headers)
        handle = urllib2.urlopen(req)
        # text should be "<html></html>"
        text = handle.read()

        # 4. press 'submit' buttom in form first form
        data = urllib.urlencode({'op': 'a_login_attempt'})
        req = urllib2.Request(self.vkhost + '/login.php', data, headers)
        handle = urllib2.urlopen(req)
        # text shoul be 'vklogin' ?
        text = handle.read()

        # 5.actually submit login form. Get s-value.
        data = urllib.urlencode({'email': self.email, 'pass': self.password,
                                 'expire': '', 'vk': ''})
        req = urllib2.Request(self.vkloginhost + '/?act=login', data, headers)
        handle = urllib2.urlopen(req)
        text = handle.read()

        match = re.search(r"name='s' value='(.*?)'", text)
        if match:
            svalue = match.group(1)
        else:
            raise VKError("s-value not returned.")

        #6. send s-value. receive "remixsid" cookie
        data = urllib.urlencode({'op': 'slogin', 'redirect': '1',
                                 'expire': '0', 'to': '', 's': svalue})
        req = urllib2.Request(self.vkhost + '/login.php', data, headers)
        handle = urllib2.urlopen(req)
        # text should be index page content
        text = handle.read()

        # "remixsid" received?
        if not filter(lambda c: c.domain == '.vkontakte.ru' and
                      c.name == 'remixsid' and c.value != 'nonenone',
                      self.cookiejar):
            raise VKError('remixsid is not returned')


class DummyVKConnector:
    """Emulator of connector to vkontakte site.

    Implements VKConnector interface.
    Acts like real VKConnector, but uses files in some directory
    instead of real web site. Useful for testing.

    """
    def __init__(self, email=None, password=None, cookiestring=''):
        self.cookiestring = cookiestring
        self.path = "file://" + os.path.join(os.path.dirname(__file__),
                                             "testdata")

    def get_page(self, path):
        host = '%s%s' % (self.path, path)
        conn = urllib2.Request(host, None, {})
        text = urllib2.urlopen(conn).read().decode('UTF-8')
        return text

    def get_cookie(self):
        return self.cookiestring

    def login(self):
        pass

    def relogin(self):
        pass
