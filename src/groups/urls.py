try:
    from django.conf.urls import url as _url
except ImportError:
    from django.urls import re_path as _url
from groups import views

urlpatterns = [
    _url(r'^$', views.group, name='management_group'),
    _url(r'^upsert$', views.upsert, name='upsert_group'),
    _url(r'^delete$', views.delete, name='delete_group'),
]
