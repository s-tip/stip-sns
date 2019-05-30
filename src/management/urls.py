from django.conf.urls import url
from management import views

urlpatterns = [
    url(r'^user/$', views.user, name='management_user'),
    url(r'^sns_config/$', views.sns_config, name='sns_config'),
    url(r'^modify_attck_information/$', views.modify_attck_information, name='modify_attck_information'),
    url(r'^reboot_slack_thread/$', views.reboot_slack_thread, name='reboot_slack_thread'),
]
