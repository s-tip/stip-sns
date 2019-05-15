from django.conf.urls import url

from api.v1 import views

urlpatterns = [
    url(r'^post$', views.post, name='post'),
]
