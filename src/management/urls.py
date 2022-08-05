try:
    from django.conf.urls import url as _url
except ImportError:
    from django.urls import re_path as _url
from management import views

urlpatterns = [
    _url(r'^sns_config/$', views.sns_config, name='sns_config'),
    _url(r'^modify_attck_information/$', views.modify_attck_information, name='modify_attck_information'),
    _url(r'^reboot_slack_thread/$', views.reboot_slack_thread, name='reboot_slack_thread'),
]
