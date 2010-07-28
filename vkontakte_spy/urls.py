from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^run_parsersfuncs/$', 'vkontakte_spy.views.run_parsersfuncs_view', name='run_parsersfuncs'),
)