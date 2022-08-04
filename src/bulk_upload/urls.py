try:
    from django.conf.urls import url as _url
except ImportError:
    from django.urls import re_path as _url
from bulk_upload import views

urlpatterns = [
    _url(r'^$', views.entry, name='bulk_upload_entry'),
    _url(r'^post/$', views.post, name='bulk_upload_post'),
]