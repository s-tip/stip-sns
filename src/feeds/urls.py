from django.conf.urls import url

# from bootcamp.feeds import views
from feeds import views

urlpatterns = [
    url(r'^$', views.feeds, name='feeds'),
    url(r'^post/$', views.post, name='post'),
    url(r'^like/$', views.like, name='like'),
    url(r'^comment/$', views.comment, name='comment'),
    url(r'^attach/$', views.attach, name='attach'),
    url(r'^load/$', views.load, name='load'),
    url(r'^check/$', views.check, name='check'),
    url(r'^check_via_poll/$', views.check_via_poll, name='check_via_poll'),
    url(r'^load_new/$', views.load_new, name='load_new'),
    url(r'^update/$', views.update, name='update'),
    url(r'^track_comments/$', views.track_comments, name='track_comments'),
    url(r'^remove/$', views.remove, name='remove_feed'),
    url(r'^download_stix/$', views.download_stix, name='download_stix'),
    url(r'^is_exist_indicator/$', views.is_exist_indicator, name='is_exist_indicator'),
    url(r'^download_csv/$', views.download_csv, name='download_csv'),
    url(r'^download_pdf/$', views.download_pdf, name='download_pdf'),
    url(r'^get_ctim_gv_url/$', views.get_ctim_gv_url, name='get_ctim_gv_url'),
    url(r'^share_misp/$', views.share_misp, name='share_misp'),
    url(r'^sighting_splunk$', views.sighting_splunk, name='sighting_splunk'),
    url(r'^create_sighting_object$', views.create_sighting_object, name='create_sighting_object'),
    url(r'^call_jira/$', views.call_jira, name='call_jira'),
    url(r'^run_phantom_playbook/$', views.run_phantom_playbook, name='run_phantom_playbook'),
    url(r'^get_like_comment/$', views.get_like_comment, name='get_like_comment'),
    url(r'^confirm_indicator/$', views.confirm_indicator, name='confirm_indicator'),
    url(r'^tags/$', views.tags, name='tags'),
    url(r'^id/(?P<pk>\S+)/$', views.feed, name='feed'),
]
