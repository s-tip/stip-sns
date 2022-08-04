try:
    from django.conf.urls import url as _url
except ImportError:
    from django.urls import re_path as _url

# from bootcamp.messenger import views
from messenger import views

urlpatterns = [
    _url(r'^$', views.inbox, name='inbox'),
    _url(r'^new/$', views.new, name='new_message'),
    _url(r'^send/$', views.send, name='send_message'),
    _url(r'^delete/$', views.delete, name='delete_message'),
    _url(r'^users/$', views.users, name='users_message'),
    _url(r'^check/$', views.check, name='check_message'),
    _url(r'^(?P<username>[^/]+)/$', views.messages, name='messages'),
]
