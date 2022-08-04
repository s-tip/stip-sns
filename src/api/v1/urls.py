try:
    from django.conf.urls import url as _url
except ImportError:
    from django.urls import re_path as _url

from api.v1 import views

urlpatterns = [
    _url(r'^post$', views.post, name='post'),
]
