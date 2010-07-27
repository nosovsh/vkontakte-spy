from django.contrib import admin
from django import forms

from vkontakte_spy import models


def vkuser_avatar(vkuser):
    """Render image of user."""
    if vkuser.image:
        return '<img width="30" src="%s">' % vkuser.image.url

vkuser_avatar.allow_tags = True
vkuser_avatar.admin_order_field = 'surname'


def news_avatar(news):
    """Render image of user for news item."""
    if news.vkuser.image:
        return '<img width="30" src="%s"> %s %s' % (news.vkuser.image.url,
                                    news.vkuser.name, news.vkuser.surname)

news_avatar.allow_tags = True
news_avatar.admin_order_field = 'vkuser'


class AccountAdminForm(forms.ModelForm):
    password = forms.CharField(required=False, max_length=200,
                               widget=forms.PasswordInput)

    class Meta:
        model = models.Account


class AccountAdmin(admin.ModelAdmin):
    form = AccountAdminForm


class NewsAdmin(admin.ModelAdmin):
    def textnouser_html(self, news):
        return news.textnouser
    textnouser_html.allow_tags = True

    list_display = ('date', 'type', news_avatar, 'textnouser_html', )
    list_filter = ('type', 'vkuser', )
    list_select_related = True
    search_fields = ('textnouser', )
    search_fields_verbose = ('textnouser', )

    fieldsets = (
            (None, {
                'fields': ('date', 'vkuser', 'type', 'textnouser', ),
            }),
            ('Advanced options', {
                'classes': ('collapse-closed', ),
                'fields': ('text', 'raw', ),
            }),
        )


class VKUserAdmin(admin.ModelAdmin):
    list_display = (vkuser_avatar, 'name', 'surname', 'isfriend', )
    list_filter = ('groups', 'isfriend', )
    search_fields = ('name', 'surname', )
    search_fields_verbose = ('name', 'surname', )


admin.site.register(models.News, NewsAdmin)
admin.site.register(models.VKGroup)
admin.site.register(models.VKUser, VKUserAdmin)
admin.site.register(models.Timetable)
admin.site.register(models.Account, AccountAdmin)
