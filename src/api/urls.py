from django.conf.urls import include
try:
    from django.conf.urls import url as _url
except ImportError:
    from django.urls import re_path as _url

urlpatterns = [
    _url(r'^v1/', include('api.v1.urls')),
]
