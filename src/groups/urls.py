from django.conf.urls import url
from groups import views

urlpatterns = [
    url(r'^$', views.group, name='management_group'),
    url(r'^upsert$', views.upsert, name='upsert_group'),
    url(r'^delete$', views.delete, name='delete_group'),
]
