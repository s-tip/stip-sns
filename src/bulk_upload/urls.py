from django.conf.urls import url
from bulk_upload import views

urlpatterns = [
    url(r'^$', views.entry, name='bulk_upload_entry'),
    url(r'^post/$', views.post, name='bulk_upload_post'),
]