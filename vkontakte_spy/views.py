from datetime import datetime, timedelta

from django.core.urlresolvers import get_callable
from django.http import HttpResponse

from vkontakte_spy.models import Timetable
from vkontakte_spy.connectors import VKConnector as Connector
from vkontakte_spy import parsers


def run_parsersfuncs():
    """Run all required parsers functions."""
    tasks = Timetable.objects.select_related()
    # dict of cookiestrings for all accounts
    cookiestrings = {}
    for task in tasks:
        if datetime.now() <= (task.last_update +
                               timedelta(seconds=task.interval)):
            continue
        cookiestring = cookiestrings.get(task.account.pk,
                                         task.account.cookiestring)
        connector = Connector(email=task.account.email,
                              password=task.account.password,
                              cookiestring=cookiestring)
        parse_func = get_callable(task.parserfunc)
        parse_func(connector)
        task.last_update = datetime.now()
        task.account.cookiestring = connector.get_cookie()
        cookiestrings[task.account.pk] = task.account.cookiestring
        task.account.save()
        task.save()


def run_parsersfuncs_view(request):
    run_parsersfuncs()
    return HttpResponse('')
