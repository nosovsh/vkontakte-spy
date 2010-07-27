"""Functions-connectors between parsers and Django.

They can connect to vkontakte web site, parse data and save it to
database using Django models.

TODO: reduce SQL queries
"""
from pprint import pprint as pp

from vkontakte_spy import models, parsers


def parsefriends(connector):
    """Save friends using `vkontakte_spy.parsers.VKFriendsParser`."""
    friends, groups = parsers.VKFriendsParser(connector).parse()
    groupsobj = {}
    for group in groups:
        groupsobj[group['id']] = models.VKGroup(**group)
        groupsobj[group['id']].save()
    for friend in friends:
        # universities are not supported yet.
        del friend['universityid']
        grouplist = friend['groups']
        del friend['groups']
        friend['isfriend'] = True
        f = models.VKUser(**friend)
        f.save()
        [f.groups.add(g) for g in grouplist]


def parsenews(connector):
    """Save news using `vkontakte_spy.parsers.VKNewsParser`."""
    try:
        lastdate = models.News.objects.latest().date
        lastitems = models.News.objects.filter(date=lastdate).values()
    except models.News.DoesNotExist:
        lastdate = None
        lastitems = []
    news = parsers.VKNewsParser(connector).parse(lastdate=lastdate,
                                                 lastitems=lastitems)
    for n in news:
        if 'vkuser_pk' in n:
            n['vkuser'], created = models.VKUser.objects.get_or_create(
                                                        pk=n['vkuser_pk'])
            del n['vkuser_pk']
        elif 'vkuser_nickname' in n:
            n['vkuser'], created = models.VKUser.objects.get_or_create(
                                                nickname=n['vkuser_nickname'])
            del n['vkuser_nickname']
        models.News(**n).save()
