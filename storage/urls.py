from django.conf import settings
from django.conf.urls import patterns, url


urlpatterns = patterns(
    'storage.views',
    url(r'^$', 'index'),
    url(r'^upload/?$', 'upload', name='upload'),
    url(r'^resize/(\d+)/(\d+)/(\d+)/?$', 'resize', name='resize'))

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        url(r'^uploads/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT, 'show_indexes': True}))
