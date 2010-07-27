#-*-coding:utf-8-*-
"""
Tools for parsing different types of pages from vkontakte web site
"""

import re
import os
import time
import datetime
from pprint import pprint

from BeautifulSoup import BeautifulSoup


class VKParserError(Exception):
    """Parser could not parse given text."""
    def __init__(self, reason, exception_original=None):
        self.args = reason,
        self.reason = reason
        self.exception_original = exception_original

    def __str__(self):
        return '<ParserException %s>' % self.reason


class VKNewsParser(object):
    """Parse news from /newsfeed.php ."""
    def __init__(self, vkconnector):
        self.vkconnector = vkconnector
        self.pagecount = None
        self.itemsonpage = 50
        self.newsfeedpath = '/newsfeed.php'

    def parse(self, lastdate=None, lastitems=[]):
        """Parse news.

        Parameters:
            'lastdate' - datetime.datetime object.
            'lastitems' - list of news items. Each item is dictionary
            with 'raw' key, where raw data of news item is kept

        -If 'lastdate' provided, return news which dates are equal or
            newer, than 'lastdate'
        -If 'lastdate' and 'lastitems' provided, return news which
            dates are newer,than 'lastdate'
            or witch dates are equal to 'lastdate' and 'raw' data is not
            exists in 'lastitems' items.
        -If 'lastdate' and 'lastitems' omitted, only last available
            news item returned.


        Return list of news items.
        Each element of returned list is dictionary with the following keys:
            'date': date of news item,
            'vkuser_pk': id of vkontakte user, initiator of news item,
            'vkuser_nickname': nickname of vkontakte user,
            'type': type of news item(photos,video,application etc.)
            'text': text,
            'textnouser': text field without link to vkuser
            'raw': raw text of news item without any changes

        Raises VKParserError if html could not be parsed.

        """
        start = 0
        news = []
        newsitem_cands = []
        while True:
            text = self.vkconnector.get_page('%s?offset=%s' %
                                             (self.newsfeedpath, start))
            try:
                tempnews = self.parsepage(text)
            except (TypeError, AttributeError, KeyError) as e:
                raise VKParserError('Parser could not parse that text', e)
            for newsitem in tempnews:
                # select only news, that user requests
                if lastdate:
                    if newsitem['date'] > lastdate:
                        news.append(newsitem)
                    elif newsitem['date'] == lastdate:
                        newsitem_cands.append(newsitem)
                    else:
                        for newsitem_cand in newsitem_cands:
                            present = 0
                            for lastitem in lastitems:
                                if lastitem['raw'] == newsitem_cand['raw']:
                                    present = 1
                                    break
                            if not present:
                                news.append(newsitem_cand)
                        return news
                # select only last group of news with the same date
                else:
                    if news:
                        if news[0]['date'] == newsitem['date']:
                            news.append(newsitem)
                        else:
                            return news
                    else:
                        news.append(newsitem)
            start += self.itemsonpage
            if not self.pageexists(text, start):
                return news

    def parsepage(self, text):
        """Parse given 'text'.

        Return list of news items in same format as 'parse' method.

        """
        soup = BeautifulSoup(text)
        news = []
        for datetag in soup.findAll('div', 'feedDayWrap'):
            date = datetag.div.renderContents().decode('utf-8')
            for newstag in datetag.findNextSibling('div').findAll('table'):
                newsitem = {}
                newsitem['raw'] = newstag.renderContents().decode('utf-8')
                type_arr = re.match(r'images/icons/(.*?)_s.gif',
                        newstag.tr.find('td', 'feedIconWrap').div.img['src'])
                newsitem['type'] = (type_arr and type_arr.group(1) or
                                   'application')
                newsitem['text'] = newstag.tr.find('td', 'feedStory').\
                                   renderContents().decode('utf-8').strip()
                #special case when one application is added by many users
                if newsitem['text'][0:2] != '<a':
                    newsitem['textnouser'] = abslinks(
                        u" добавил(а) приложение " +
                        newstag.tr.find('td', 'feedStory').a.decode('utf-8'),
                        self.vkconnector.vkhost)
                    #iterate all users in that news item
                    for musertag in newstag.tr.find('td', 'feedStory').a.\
                                                        findNextSiblings('a'):
                        newsitem = newsitem.copy()
                        # id or nikname in link?
                        # TODO: this is very stupid way
                        if musertag['href'][:3] == '/id':
                            newsitem['vkuser_pk'] = int(musertag['href'][3:])
                        else:
                            newsitem['vkuser_nickname'] = musertag['href'][1:]
                        newsitem['text'] = abslinks(unicode(musertag) +
                                                    newsitem['textnouser'],
                                                    self.vkconnector.vkhost)
                        newsitem['date'] = datetime.datetime.strptime(
                            rus2eng(date) + " " + time, "%d %B %Y %H:%M")
                        news.append(newsitem)
                    continue
                # id or nikname in link?
                # TODO: this is very stupid way
                if newstag.tr.find('td', 'feedStory').a['href'][:3] == '/id':
                    newsitem['vkuser_pk'] = int(newstag.tr.find('td',
                                                'feedStory').a['href'][3:])
                else:
                    newsitem['vkuser_nickname'] = newstag.tr.find('td',
                                                'feedStory').a['href'][1:]
                newstag.tr.find('td', 'feedStory').a.extract()
                newsitem['textnouser'] = abslinks(newstag.tr.find('td',
                        'feedStory').renderContents().decode('utf-8').strip(),
                        self.vkconnector.vkhost)
                time = newstag.tr.find('td', 'feedTime').div.renderContents().\
                                                                decode('utf-8')
                newsitem['date'] = datetime.datetime.strptime(rus2eng(date) +
                                                " " + time, "%d %B %Y %H:%M")
                news.append(newsitem)
        return news

    def pageexists(self, text, start):
        """True if link to page in 'text' with 'start' parameter exists."""
        if text.find('onclick="return getPage(' + str(start) + ')"') == -1:
            return False
        return True


def rus2eng(str):
    """Translate russian strings from vkontakte to english"""
    arr = {
    u'в ': u'',

    u'января': u'january',
    u'февраля': u'february',
    u'марта': u'march',
    u'апреля': u'april',
    u'мая': u'may',
    u'июня': u'june',
    u'июля': u'july',
    u'августа': u'august',
    u'сентября': u'september',
    u'октября': u'october',
    u'ноября': u'november',
    u'декабря': u'december',

    u'сегодня': datetime.date.today().strftime("%d %B %Y"),
    u'вчера': (datetime.date.today() -
               datetime.timedelta(1)).strftime("%d %B %Y"),

    u'янв': u'january',
    u'фев': u'february',
    u'мар': u'march',
    u'апр': u'april',
    u'мая': u'may',
    u'июн': u'june',
    u'июл': u'july',
    u'авг': u'august',
    u'сен': u'september',
    u'окт': u'october',
    u'ноя': u'november',
    u'дек': u'december',
    }
    for x, y in arr.items():
        if x in str:
            str = str.replace(x, y)

    return str


def abslinks(text, domain):
    """Add domain to all links whithout domain in text"""
    def abs(matchobj):
        returntemplate = 'href="%s"'
        if matchobj.group(1).startswith('http://'):
            return returntemplate % matchobj.group(1)
        elif matchobj.group(1).startswith('/'):
            return returntemplate % (domain + matchobj.group(1))
        else:
            return returntemplate % (domain + "/" + matchobj.group(1))
    return re.sub(r'href="(.*?)"', abs, text)


class VKFriendsParser(object):
    """Parse friend list and groups of friends from /friends.php."""
    itemsonpage = 20

    def __init__(self, vkconnector):
        self.vkconnector = vkconnector
        self.pagecount = None
        self.path = '/friends.php'

    def parse(self):
        """Parse friends.

        Parse data and return list with two elements: friends and groups.
        Friends is a list of dictionaries wuth folowing keys:
            -'id'
            -'name'
            -'surname'
            -'nickname'
            -'avatar': path to avatar
            -'rod'
            -'univercityid'
            -'groups':[list of group ids]}

         Format of groups dictionaries:
             -'id'
             -'name'

        """
        text = self.vkconnector.get_page(self.path)
        try:
            # friends
            re_friends = re.compile(r'''
            \[                                       #openning bracket
              (?:
                (?P<id>\d*),                         #user id
                "(?P<name>\S*)\ (?P<surname>[^,]*)", #user name and surname
                "(?P<image>[^,\n]*?)",               #avatar
                (?:[^,\n]*?),                        #some shit
                "(?P<nickname>[^,\n]*?)",            #nickname
                "(?P<rod>[^,\n]*?)",                 #Parent case...
                (?:[^,\n]*?),                        #some shit
                (?:[^,\n]*?),                        #some shit
                (?P<universityid>\d*?),              #university
                (?:[^,\n]*?),                        #some shit
                (?:[^,\n]*?)                         #some shit
              )
            \]                                      #closing bracket
            ''', re.VERBOSE)
            friends_iter = re.finditer(re_friends, text)

            # groups
            # find part of text where groups list exists
            groups_text = re.search(r'friendsLists = .*?[[cat_id => name]]',
                                    text)
            # parse groups
            groups_re = re.compile(r'"(?P<id>\d+)":"(?P<name>.*?)"')
            groups_iter = re.finditer(groups_re, groups_text.group(0))
            # format groups
            groups = map(lambda x: x.groupdict(), groups_iter)

            # what friends in what groups
            re_friendgroups = re.compile(r'"(?P<id>[\d]+)":(?P<mask>[\d]+)')
            friendgroups_list = list(re.finditer(re_friendgroups, text))

            def formatfriendsdict(f):
                """Friends formating"""
                friend = f.groupdict()
                mask = filter(lambda x: x.group('id') == friend['id'],
                              friendgroups_list)[0].group('mask')
                friendgroup_dict = filter(lambda x: int(mask) &
                                          (1 << int(x['id'])), groups)
                friend['groups'] = map(lambda x: int(x['id']),
                                       friendgroup_dict)
                friend['image'] = friend['image'].replace('\\', '')
                return friend
            friends = map(formatfriendsdict, friends_iter)

            return friends, groups

        except (TypeError, AttributeError, KeyError, ValueError) as e:
            raise VKParserError('Parser could not parse text with mail', e)
