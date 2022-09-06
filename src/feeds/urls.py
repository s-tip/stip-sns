try:
    from django.conf.urls import url as _url
except ImportError:
    from django.urls import re_path as _url

# from bootcamp.feeds import views
from feeds import views

urlpatterns = [
    _url(r'^$', views.feeds, name='feeds'),
    _url(r'^post/$', views.post, name='post'),
    _url(r'^like/$', views.like, name='like'),
    _url(r'^comment/$', views.comment, name='comment'),
    _url(r'^attach/$', views.attach, name='attach'),
    _url(r'^load/$', views.load, name='load'),
    _url(r'^check/$', views.check, name='check'),
    _url(r'^check_via_poll/$', views.check_via_poll, name='check_via_poll'),
    _url(r'^load_new/$', views.load_new, name='load_new'),
    _url(r'^update/$', views.update, name='update'),
    _url(r'^track_comments/$', views.track_comments, name='track_comments'),
    _url(r'^remove/$', views.remove, name='remove_feed'),
    _url(r'^download_stix/$', views.download_stix, name='download_stix'),
    _url(r'^is_exist_indicator/$', views.is_exist_indicator, name='is_exist_indicator'),
    _url(r'^download_csv/$', views.download_csv, name='download_csv'),
    _url(r'^download_pdf/$', views.download_pdf, name='download_pdf'),
    _url(r'^get_ctim_gv_url/$', views.get_ctim_gv_url, name='get_ctim_gv_url'),
    _url(r'^share_misp/$', views.share_misp, name='share_misp'),
    _url(r'^sighting_splunk$', views.sighting_splunk, name='sighting_splunk'),
    _url(r'^create_sighting_object$', views.create_sighting_object, name='create_sighting_object'),
    _url(r'^call_jira/$', views.call_jira, name='call_jira'),
    _url(r'^run_phantom_playbook/$', views.run_phantom_playbook, name='run_phantom_playbook'),
    _url(r'^get_like_comment/$', views.get_like_comment, name='get_like_comment'),
    _url(r'^confirm_indicator/$', views.confirm_indicator, name='confirm_indicator'),
    _url(r'^modify_sns_filter/$', views.modify_sns_filter, name='modify_sns_filter'),
    _url(r'^tags/$', views.tags, name='tags'),
    _url(r'^id/(?P<pk>\S+)/$', views.feed, name='feed'),
]
