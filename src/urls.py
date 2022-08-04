from django.conf import settings
from django.conf.urls import include
try:
    from django.conf.urls import url as _url
except ImportError:
    from django.urls import re_path as _url
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from activities import views as activities_views
from core import views as core_views
from search import views as search_views
from django.views.i18n import JavaScriptCatalog


urlpatterns = [
    _url(r'^$', core_views.home, name='home'),
    _url(r'^login/', core_views.login, name='login'),
    _url(r'^login_totp/', core_views.login_totp, name='login_totp'),
    _url(r'^logout', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    _url(r'^settings/$', core_views.settings, name='settings'),
    _url(r'^management/', include('management.urls')),
    _url(r'^settings/picture/$', core_views.picture, name='picture'),
    _url(r'^settings/upload_picture/$', core_views.upload_picture, name='upload_picture'),
    _url(r'^settings/save_uploaded_picture/$', core_views.save_uploaded_picture, name='save_uploaded_picture'),
    _url(r'^settings/password/$', core_views.password, name='password'),
    _url(r'^settings/password_modified/$', core_views.password_modified, name='password_modified'),
    _url(r'^settings/get_administrative_area/$', core_views.get_administrative_area, name='administrative_area'),
    _url(r'^settings/get_2fa_secret/$', core_views.get_2fa_secret, name='get_2fa_secret'),
    _url(r'^settings/enable_2fa/$', core_views.enable_2fa, name='enable_2fa'),
    _url(r'^settings/disable_2fa/$', core_views.disable_2fa, name='disable_2fa'),
    _url(r'^network/$', core_views.network, name='network'),
    _url(r'^feeds/', include('feeds.urls')),
    _url(r'^groups/', include('groups.urls')),
    _url(r'^messages/', include('messenger.urls')),
    _url(r'^bulk_upload/', include('bulk_upload.urls')),
    _url(r'^api/', include('api.urls')),
    _url(r'^notifications/$', activities_views.notifications, name='notifications'),
    _url(r'^notifications/last/$', activities_views.last_notifications, name='last_notifications'),
    _url(r'^notifications/check/$', activities_views.check_notifications, name='check_notifications'),
    _url(r'^search/$', search_views.search, name='search'),
    _url(r'^jsi18n/$', JavaScriptCatalog.as_view()),
    _url(r'^(?P<username>[^/]+)/$', core_views.profile, name='profile')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
