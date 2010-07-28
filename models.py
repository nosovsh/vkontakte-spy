import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from BeautifulSoup import BeautifulSoup

import vkontakte_spy


class Account(models.Model):
    """Vkontakte account."""
    vkuser_id = models.IntegerField(_('vkontakte user id'), blank=True)
    user = models.ForeignKey(User, verbose_name=_('user'))
    email = models.EmailField(_('e-mail'))
    password = models.CharField(_('password'), max_length=200)
    cookiestring = models.TextField(_('cookie string'), blank=True,
                                help_text=_('can be filled automatically'))

    def __unicode__(self):
        return "%s (%s)" % (unicode(self.vkuser_id), unicode(self.user.id))


class Timetable(models.Model):
    """Timetable of parsing."""
    parserfunc = models.CharField(_('parser function'), max_length=400,
                                  choices=vkontakte_spy.parsersfuncs_list)
    account = models.ForeignKey(Account, verbose_name=_('account'))
    interval = models.IntegerField(_('interval'), default=3600,
                    help_text=_('Time interval between parsing. In seconds.'))
    last_update = models.DateTimeField(_('last update'),
                                       default=datetime.datetime.now)

    def __unicode__(self):
        return "%s (%s)" % (self.parserfunc, unicode(self.account))

    class Meta:
        verbose_name_plural = "timetable"


class VKGroup(models.Model):
    """Vkontakte group of users."""
    id = models.IntegerField(_('id'), primary_key=True)
    name = models.CharField(_('name'), max_length=300)

    def __unicode__(self):
        return self.name


class VKUser(models.Model):
    """Vkontakte user."""
    vkid = models.IntegerField(_('vkontakte id'), blank=True, null=True)
    nickname = models.CharField(_('nickname'), max_length=300,
                                default='', blank=True)
    image = models.ImageField(_('image'), upload_to="avatars")
    name = models.CharField(_('name'), max_length=300, blank=True)
    surname = models.CharField(_('surname'), max_length=300, blank=True)
    rod = models.CharField(_('rod'), max_length=300, blank=True)
    groups = models.ManyToManyField(VKGroup, verbose_name=_('groups'),
                                    blank=True)
    isfriend = models.BooleanField(_('friend?'))

    def __unicode__(self):
        return "%s %s (%s)" % (self.name, self.surname, self.id)


class News(models.Model):
    """Friends news"""
    TYPES = (
            ('photos', 'Photos'),
            ('video', 'Video'),
            ('notesplus', 'Notes'),
            ('topics', 'Topics'),
            ('people', 'People'),
            ('friends', 'Friends'),
            ('groups', 'Groups'),
            ('events', 'Events'),
            ('audio', 'Audio'),
            ('application', 'Apps'),
            ('tags', 'Tags'),
            ('pages', 'Pages'),
            ('gifts', 'Gifts'),
    )
    date = models.DateTimeField(_('date'))
    vkuser = models.ForeignKey(VKUser, verbose_name=_('vkontakte user'))
    type = models.CharField(_('type'), max_length=50,
                            choices=TYPES, blank=False)
    text = models.TextField(_('text'))
    textnouser = models.TextField(_('text without user'))
    raw = models.TextField(_('raw text'),
                        help_text=_('Original text without any convertions.'))

    def __unicode__(self):
        return "%s: %s" % (unicode(self.date), self.type)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "news"
        get_latest_by = "date"
