Vkontakte-spy is a Python library that allows users to parse and save
newsfeed from Vkontakte web site (http://vkontakte.ru, http://vk.com).
Vkontakte doesn't allow users to save newsfeed in any convenient format.
You can only visit web interface: http://vkontakte.ru/newsfeed.php .
But what if you want to use RSS or receive news by email?
Goal of vkontakte-spy is to free information from slavery.

There are two ways of using vkontakte spy: as Django application and as a
standalone Python package. 

============
Installation
============

I. Django application:

    1. Add ``vkontakte-spy`` to your ``PYTHONPATH``
    (eg. ``python setup.py install``)
    2. Add ``vkontakte-spy`` to your ``INSTALLED_APPS``
    3. Run ``python manage.py syncdb``
    4. Add ``python manage.py run_parsersfuncs`` to your cron jobs.
    Or you can add ``vkontakte_spy.urls`` to your site urls and visit
    ``/run_parsersfuncs`` as often as you want.

II. Standalone package:
	
	1. Add ``vkontakte-spy`` to your ``PYTHONPATH``
	(eg. ``python setup.py install``)
	

=====
Usage
=====

I. Django application:
	
	1. Visit your admin site.
	2. Add your vkontakte account information to ``Accounts`` table.
	3. Add tasks to ``Timetable`` table. You should select what parser
	and how often should work.
	4. Wait until your cron runs or visit ``/run_parsersfuncs`` url.
	5. Explore content of ``News``, ``VKGroup`` and ``VKUser`` tables
	at admin site. Now all your vkontakte news and friends will be here.
	You can do what you want with them.
	
II. Standalone package:

	Example::
	
		from datetime import datetime
		
		from vkontakte_spy import connectors, parsers
		
		
		c = connectors.VKConnector(email='your email',
								password='your password')
		newsparser = parsers.VKNewsParser(c)
		# get last news item
		news = newsparser.parse()
		# get news items, created later than noon of July 03 2010 
		news = newsparser.parse(lastdate=datetime(2010, 05, 03, 12, 00))
		# There could be a situation when at one minute multiple news items
		# created. But at your last parsing you've saved only one of them.
		# So you can pass content of that news item to not to save it again.
		news = newsparser.parse(lastdate=datetime(2010, 05, 03, 12, 00),
								lastitems=[{'raw': 'newscontent'},])
								
		friendsparser = parsers.VKFriendsParser(c)
		# get all your friends and groups of friends
		friends, groups = friendsparser.parse()
		
		# get cookies that was accepted after log in to vkontakte site.
		cookiestring = c.get_cookie()
		# now you can initialize VKConnector using this string. 
		# And now connector will not log in again. 
		c = connectors.VKConnector(email='your email',
								password='your password',
								cookiestring=cookiestring)


==================
Writing extensions
==================

You can write your own parser functions that will parse some other
vkontakte pages and save them to database. Look at 
``vkontakte_spy.parsersfuncs`` for examples.
Then you can add them to ``vkontakte_spy.parsersfuncs_list`` and they
will appear in Timetable model at admin site. Look at ``vkontakte_spy.__init__``
for examples.
