#-*-coding:utf-8-*-
import datetime
from pprint import pprint as pp
from django.test import TestCase

from vkontakte_spy import parsers, connectors


class ParsersTests(TestCase):
    def test_rus2eng(self):
        self.failUnlessEqual(parsers.rus2eng('18 июля 2010'.decode('utf-8')),
                            '18 july 2010')

    def test_rus2eng_today(self):
        self.failUnlessEqual(parsers.rus2eng('сегодня'.decode('utf-8')),
                            datetime.date.today().strftime("%d %B %Y"))

    def test_rus2eng_yesterday(self):
        self.failUnlessEqual(parsers.rus2eng('вчера'.decode('utf-8')),
                            (datetime.date.today() -
                             datetime.timedelta(1)).strftime("%d %B %Y"))

    def test_abslinks(self):
        text = '<a class="memLink" href="/id123456">User</a> добавила приложение <a href="/app123456">Application</a>.'
        text_final = '<a class="memLink" href="http://vkontakte.ru/id123456">User</a> добавила приложение <a href="http://vkontakte.ru/app123456">Application</a>.'
        self.failUnlessEqual(parsers.abslinks(text.decode('utf-8'),
                        'http://vkontakte.ru'), text_final.decode('utf-8'))


class VKNewsParserTest(TestCase):
    def setUp(self):
        self.vkconnector = connectors.DummyVKConnector()
        self.parser = parsers.VKNewsParser(self.vkconnector)

    def test_pageexists_true(self):
        text = '<ul class="pageList"><li class="current">1</li><li><a href="newsfeed.php?section=&offset=50" onclick="return getPage(50)">2</a></li><li><a href="newsfeed.php?section=&offset=100" onclick="return getPage(100)">3</a></li>'
        self.assertTrue(self.parser.pageexists(text, 50))

    def test_pageexists_false(self):
        text = '<ul class="pageList"><li class="current">1</li><li><a href="newsfeed.php?section=&offset=50" onclick="return getPage(50)">2</a></li><li><a href="newsfeed.php?section=&offset=100" onclick="return getPage(100)">3</a></li>'
        self.assertFalse(self.parser.pageexists(text, 300))

    def test_parsepage(self):
        text = texts[0]
        self.failUnlessEqual(len(self.parser.parsepage(text)), 2)

    def test_parsepage_date(self):
        text = texts[0]
        news = self.parser.parsepage(text)
        date = datetime.datetime.now().replace(hour=12, minute=15, second=0,
                                               microsecond=0)
        self.failUnlessEqual(news[0]['date'], date)

    def test_parsepage_date(self):
        text = texts[0]
        news = self.parser.parsepage(text)
        date = datetime.datetime.now().replace(hour=12, minute=15, second=0,
                                               microsecond=0)
        self.failUnlessEqual(news[0]['date'], date)

    def test_parsepage_type(self):
        text = texts[0]
        news = self.parser.parsepage(text)
        self.failUnlessEqual(news[1]['type'], 'friends')

    def test_parsepage_vkuser_pk(self):
        text = texts[0]
        news = self.parser.parsepage(text)
        self.failUnlessEqual(news[1]['vkuser_pk'], 9374)

    def test_parsepage_row(self):
        text = texts[0]
        news = self.parser.parsepage(text)
        raw = u"""\n<tr>\n<td class="feedIconWrap">\n<div><img class="feedIcon" src="images/icons/friends_s.gif?2" /></div>\n</td>\n<td class="feedStory">\n<a class="memLink" href="/id9374">User2</a> \u0434\u043e\u0431\u0430\u0432\u0438\u043b 2 \u0434\u0440\u0443\u0437\u0435\u0439: <div class="feedFriends"><div class="feedFriend">\n<div class="feedFriendImg">\n<a href="/user3"><img src="http://cs9934.vkontakte.ru/u2345/c_g2d123.jpg" /></a>\n</div>\n<div class="feedFriendText">\n<a href="/user3">User3Surname<br /><small>User3Name</small></a>\n</div>\n</div><div class="feedFriend">\n<div class="feedFriendImg">\n<a href="/id34523"><img src="http://cs1345.vkontakte.ru/u24235/c_45dg13.jpg" /></a>\n</div>\n<div class="feedFriendText">\n<a href="/id34523">User4Surname<br /><small>User4Name</small></a>\n</div>\n</div></div>\n</td>\n<td class="feedTime">\n<div>12:05</div>\n</td>\n</tr>\n"""
        self.failUnlessEqual(news[1]['raw'], raw)

    def test_parse(self):
        self.vkconnector.text = texts[1]
        news = self.parser.parse()
        self.failUnlessEqual(len(news), 1)

    def test_parse_lastdate(self):
        self.vkconnector.text = texts[1]
        lastdate = (datetime.datetime.now() -
                datetime.timedelta(1)).replace(hour=23, minute=40, second=0,
                                               microsecond=0)
        news = self.parser.parse(lastdate=lastdate)
        self.failUnlessEqual(len(news), 4)

    def test_parse_lastdate_lastitems(self):
        self.vkconnector.text = texts[1]
        lastdate = (datetime.datetime.now() -
                datetime.timedelta(1)).replace(hour=23, minute=40, second=0,
                                               microsecond=0)
        lastitems = ({'raw': u'\n<tr>\n<td class="feedIconWrap">\n<div><img class="feedIcon" src="images/icons/friends_s.gif?2" /></div>\n</td>\n<td class="feedStory">\n<a class="memLink" href="/id57473">User10</a> \u0434\u043e\u0431\u0430\u0432\u0438\u043b\u0430 2 \u0434\u0440\u0443\u0437\u0435\u0439: <div class="feedFriends"><div class="feedFriend">\n<div class="feedFriendImg">\n<a href="/User4"><img src="http://cs12344.vkontakte.ru/u124124/c_342ffc3.jpg" /></a>\n</div>\n<div class="feedFriendText">\n<a href="/User4">User4<br /><small>User4</small></a>\n</div>\n</div><div class="feedFriend">\n<div class="feedFriendImg">\n<a href="/id234234"><img src="http://cs345.vkontakte.ru/u21235/c_3fc23c3.jpg" /></a>\n</div>\n<div class="feedFriendText">\n<a href="/id234234">User6<br /><small>User6</small></a>\n</div>\n</div></div>\n</td>\n<td class="feedTime">\n<div>23:40</div>\n</td>\n</tr>\n'},)
        news = self.parser.parse(lastdate=lastdate, lastitems=lastitems)
        self.failUnlessEqual(len(news), 3)

    def test_parse_error(self):
        self.vkconnector.text = '<div class="feedDayWrap"><div class="feedDay">'
        self.assertRaises(parsers.VKParserError, self.parser.parse)


class VKFriendsParserTest(TestCase):
    def setUp(self):
        self.vkconnector = connectors.DummyVKConnector()
        self.parser = parsers.VKFriendsParser(self.vkconnector)

    def test_parse_friends(self):
        self.vkconnector.text = texts[2]
        friends, groups = self.parser.parse()
        self.failUnlessEqual(len(friends), 2)

    def test_parse_groups(self):
        self.vkconnector.text = texts[2]
        friends, groups = self.parser.parse()
        self.failUnlessEqual(len(groups), 3)

    def test_parse_usergroups(self):
        self.vkconnector.text = texts[2]
        friends, groups = self.parser.parse()
        self.failUnlessEqual(friends[1]['groups'], [1, 2])

    def test_parse_error(self):
        self.vkconnector.text = 'broken text'
        self.assertRaises(parsers.VKParserError, self.parser.parse)

    def test_parse_user(self):
        self.vkconnector.text = texts[2]
        vkuser = {'groups': [],
                 'id': '14357',
                 'image': 'http://cs5345.vkontakte.ru/u12432345/b_v345vv3.jpg',
                 'name': 'User1Name',
                 'nickname': 'user1nickname',
                 'rod': 'User1rod',
                 'surname': 'User1Surname',
                 'universityid': '345'}
        friends, groups = self.parser.parse()
        self.failUnlessEqual(friends[0], vkuser)


texts = ("""<div class="feedDayWrap"><div class="feedDay">сегодня</div></div>

<div class="items_wrap">
<table class="feedTable  first" cellpadding="0" cellspacing="0" border="0">
<tr>
 <td class="feedIconWrap">
  <div><img class="feedIcon" src="images/icons/groups_s.gif?2"></div>
 </td>
 <td class="feedStory">
  <a class="memLink" href="/user1">User1</a> вступил в группу <a href='club123457'>Group1</a>.
 </td>

 <td class="feedTime">
  <div>12:15</div>
 </td>
</tr>
</table><table class="feedTable " cellpadding="0" cellspacing="0" border="0">
<tr>
 <td class="feedIconWrap">
  <div><img class="feedIcon" src="images/icons/friends_s.gif?2"></div>
 </td>
 <td class="feedStory">

    <a class="memLink" href="/id9374">User2</a> добавил 2 друзей: <div class="feedFriends"><div class="feedFriend">
  <div class="feedFriendImg">
    <a href="/user3"><img src="http://cs9934.vkontakte.ru/u2345/c_g2d123.jpg"/></a>
  </div>
  <div class="feedFriendText">
    <a href="/user3">User3Surname<br/><small>User3Name</small></a>

  </div>
</div><div class="feedFriend">
  <div class="feedFriendImg">
    <a href="/id34523"><img src="http://cs1345.vkontakte.ru/u24235/c_45dg13.jpg"/></a>
  </div>
  <div class="feedFriendText">
    <a href="/id34523">User4Surname<br/><small>User4Name</small></a>
  </div>

</div></div>
 </td>
 <td class="feedTime">
  <div>12:05</div>
 </td>
</tr>
</table>
</div>""",
"""<div class="feedDayWrap"><div class="feedDay">сегодня</div></div>

<div class="items_wrap">
<table class="feedTable  first" cellpadding="0" cellspacing="0" border="0">
<tr>
 <td class="feedIconWrap">
  <div><img class="feedIcon" src="images/icons/groups_s.gif?2"></div>
 </td>
 <td class="feedStory">
  <a class="memLink" href="/user1">User1</a> вступил в группу <a href='club123457'>Group1</a>.
 </td>

 <td class="feedTime">
  <div>12:15</div>
 </td>
</tr>
</table><table class="feedTable " cellpadding="0" cellspacing="0" border="0">
<tr>
 <td class="feedIconWrap">
  <div><img class="feedIcon" src="images/icons/friends_s.gif?2"></div>
 </td>
 <td class="feedStory">

    <a class="memLink" href="/id9374">User2</a> добавил 2 друзей: <div class="feedFriends"><div class="feedFriend">
  <div class="feedFriendImg">
    <a href="/user3"><img src="http://cs9934.vkontakte.ru/u2345/c_g2d123.jpg"/></a>
  </div>
  <div class="feedFriendText">
    <a href="/user3">User3Surname<br/><small>User3Name</small></a>

  </div>
</div><div class="feedFriend">
  <div class="feedFriendImg">
    <a href="/id34523"><img src="http://cs1345.vkontakte.ru/u24235/c_45dg13.jpg"/></a>
  </div>
  <div class="feedFriendText">
    <a href="/id34523">User4Surname<br/><small>User4Name</small></a>
  </div>

</div></div>
 </td>
 <td class="feedTime">
  <div>12:05</div>
 </td>
</tr>
</table>
</div><div class="feedDayWrap"><div class="feedDay">вчера</div></div>
<div class="items_wrap">
<table class="feedTable  first" cellpadding="0" cellspacing="0" border="0">
<tr>
 <td class="feedIconWrap">
  <div><img class="feedIcon" src="images/icons/friends_s.gif?2"></div>
 </td>
 <td class="feedStory">
    <a class="memLink" href="/id5747">User5</a> добавила 2 друзей: <div class="feedFriends"><div class="feedFriend">

  <div class="feedFriendImg">
    <a href="/User4"><img src="http://cs12344.vkontakte.ru/u124124/c_342ffc3.jpg"/></a>
  </div>
  <div class="feedFriendText">
    <a href="/User4">User4<br/><small>User4</small></a>
  </div>
</div><div class="feedFriend">
  <div class="feedFriendImg">

    <a href="/id234234"><img src="http://cs345.vkontakte.ru/u21235/c_3fc23c3.jpg"/></a>
  </div>
  <div class="feedFriendText">
    <a href="/id234234">User6<br/><small>User6</small></a>
  </div>
</div></div>
 </td>
 <td class="feedTime">

  <div>23:40</div>
 </td>
</tr>
</table><table class="feedTable  first" cellpadding="0" cellspacing="0" border="0">
<tr>
 <td class="feedIconWrap">
  <div><img class="feedIcon" src="images/icons/friends_s.gif?2"></div>
 </td>
 <td class="feedStory">
    <a class="memLink" href="/id57473">User10</a> добавила 2 друзей: <div class="feedFriends"><div class="feedFriend">

  <div class="feedFriendImg">
    <a href="/User4"><img src="http://cs12344.vkontakte.ru/u124124/c_342ffc3.jpg"/></a>
  </div>
  <div class="feedFriendText">
    <a href="/User4">User4<br/><small>User4</small></a>
  </div>
</div><div class="feedFriend">
  <div class="feedFriendImg">

    <a href="/id234234"><img src="http://cs345.vkontakte.ru/u21235/c_3fc23c3.jpg"/></a>
  </div>
  <div class="feedFriendText">
    <a href="/id234234">User6<br/><small>User6</small></a>
  </div>
</div></div>
 </td>
 <td class="feedTime">

  <div>23:40</div>
 </td>
</tr>
</table><table class="feedTable " cellpadding="0" cellspacing="0" border="0">
<tr>
 <td class="feedIconWrap">
  <div><img class="feedIcon" src="images/icons/friends_s.gif?2"></div>
 </td>
 <td class="feedStory">
  <a class="memLink" href="/user7">User7</a> добавил в друзья <a class="memLink" href="/id12312">User3</a>.
 </td>

 <td class="feedTime">
  <div>23:27</div>
 </td>
</tr>
</table><table class="feedTable " cellpadding="0" cellspacing="0" border="0">
<tr>
 <td class="feedIconWrap">
  <div><img class="feedIcon" src="images/icons/people_s.gif?2"></div>
 </td>
 <td class="feedStory">

  <a class="memLink" href="/user8">User8</a> Status.
 </td>
 <td class="feedTime">
  <div>23:19</div>
 </td>
</tr>
</table><div>""",
""" var friendsData = {'id':12345,'mid':12345,'hash':'sdlfjl2k3r','summary':"У Вас 123 друга",'friends':[[14357,"User1Name User1Surname","http:\/\/cs5345.vkontakte.ru\/u12432345\/b_v345vv3.jpg",1,"user1nickname","User1rod",0,1,345,"10",0],[3453461,"User2name User2Surname","http:\/\/cs24234.vkontakte.ru\/u363453\/b_ghb354.jpg",1,"user2nickname","User2Rod",0,1,234,"10",0]],'universities':{123:"univ1",234:"univ2",2:"univ3"}
         var friendsLists = {"1":"first","2":"second","3":"third"}; // [[cat_id => name]]
         var friendCats = {"14357":1,"3453461":7}
""")
