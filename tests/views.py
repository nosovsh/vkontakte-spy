#-*-coding:utf-8-*-
import datetime
from pprint import pprint as pp
from django.test import TestCase

from vkontakte_spy import parsers, connectors, models, views
from vkontakte_spy.tests.parsers import texts


# patching views to use connector, useful for testing
views.Connector = connectors.DummyVKConnector


class ViewsTests(TestCase):
    urls = 'vkontakte_spy.urls'
    fixtures = ['vkontakte_spy_tests.json', ]

    def test_run_parsersfuncs_news(self):
        views.Connector.text = texts[0]
        views.run_parsersfuncs()
        self.assertEqual(len(models.News.objects.all()), 1)

    def test_run_parsersfuncs_news_lastdate(self):
        vkuser = models.VKUser.objects.create(vkid=123)
        newsdate = (datetime.datetime.now() - datetime.timedelta(1)). \
                    replace(hour=23, minute=40, second=0, microsecond=0)
        models.News.objects.create(date=newsdate, vkuser=vkuser)
        views.Connector.text = texts[1]
        views.run_parsersfuncs()
        self.assertEqual(len(models.News.objects.all()), 5)

    def test_run_parserfuncs_news_lastitems(self):
        raw = u'\n<tr>\n<td class="feedIconWrap">\n<div><img class="feedIcon" src="images/icons/friends_s.gif?2" /></div>\n</td>\n<td class="feedStory">\n<a class="memLink" href="/id57473">User10</a> \u0434\u043e\u0431\u0430\u0432\u0438\u043b\u0430 2 \u0434\u0440\u0443\u0437\u0435\u0439: <div class="feedFriends"><div class="feedFriend">\n<div class="feedFriendImg">\n<a href="/User4"><img src="http://cs12344.vkontakte.ru/u124124/c_342ffc3.jpg" /></a>\n</div>\n<div class="feedFriendText">\n<a href="/User4">User4<br /><small>User4</small></a>\n</div>\n</div><div class="feedFriend">\n<div class="feedFriendImg">\n<a href="/id234234"><img src="http://cs345.vkontakte.ru/u21235/c_3fc23c3.jpg" /></a>\n</div>\n<div class="feedFriendText">\n<a href="/id234234">User6<br /><small>User6</small></a>\n</div>\n</div></div>\n</td>\n<td class="feedTime">\n<div>23:40</div>\n</td>\n</tr>\n'
        vkuser = models.VKUser.objects.create(vkid=123)
        newsdate = (datetime.datetime.now() - datetime.timedelta(1)). \
                    replace(hour=23, minute=40, second=0, microsecond=0)
        models.News.objects.create(date=newsdate, vkuser=vkuser, raw=raw)
        views.Connector.text = texts[1]
        views.run_parsersfuncs()
        self.assertEqual(len(models.News.objects.all()), 4)

    def test_run_parserfuncs_friends(self):
        task = models.Timetable.objects.get(pk=1)
        task.parserfunc = 'vkontakte_spy.parsersfuncs.parsefriends'
        task.save()
        views.Connector.text = texts[2]
        views.run_parsersfuncs()
        self.assertEqual(len(models.VKUser.objects.all()), 2)

    def test_run_parserfuncs_friends_groups(self):
        task = models.Timetable.objects.get(pk=1)
        task.parserfunc = 'vkontakte_spy.parsersfuncs.parsefriends'
        task.save()
        views.Connector.text = texts[2]
        views.run_parsersfuncs()
        self.assertEqual(len(models.VKGroup.objects.all()), 3)

    def test_run_parsersfuncs_timetable(self):
        task = models.Timetable.objects.get(pk=1)
        task.last_update = datetime.datetime.now()
        task.save()
        views.Connector.text = texts[0]
        views.run_parsersfuncs()
        self.assertEqual(len(models.News.objects.all()), 0)
