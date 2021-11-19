from django.conf.urls import url
from management import views

urlpatterns = [
    url(r'^sns_config/$', views.sns_config, name='sns_config'),
    url(r'^modify_attck_information/$', views.modify_attck_information, name='modify_attck_information'),
    url(r'^reboot_slack_thread/$', views.reboot_slack_thread, name='reboot_slack_thread'),
    url(r'^stix_customizer/set_configuration/$', views.set_stix_customizer_configuration, name='set_stix_customizer_configuration'),
    url(r'^stix_customizer/get_configuration/$', views.get_stix_customizer_configuration, name='get_stix_customizer_configuration'),
    url(r'^stix_customizer/$', views.stix_customizer, name='stix_customizer'),
]
