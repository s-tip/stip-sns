from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from activities import views as activities_views
from core import views as core_views
from search import views as search_views
import django.views.i18n

urlpatterns = [
    url(r'^$', core_views.home, name='home'),
    url(r'^login', core_views.login, name='login'),
    url(r'^logout', auth_views.logout, {'next_page': '/'}, name='logout'),
    #url(r'^signup/$', bootcamp_auth_views.signup, name='signup'),
    url(r'^settings/$', core_views.settings, name='settings'),
    url(r'^management/', include('management.urls')),
    url(r'^settings/picture/$', core_views.picture, name='picture'),
    url(r'^settings/upload_picture/$', core_views.upload_picture,
        name='upload_picture'),
    url(r'^settings/save_uploaded_picture/$', core_views.save_uploaded_picture,
        name='save_uploaded_picture'),
    url(r'^settings/password/$', core_views.password, name='password'),
    url(r'^settings/password_modified/$', core_views.password_modified, name='password_modified'),
    url(r'^settings/get_administrative_area/$', core_views.get_administrative_area, name='administrative_area'),
    url(r'^network/$', core_views.network, name='network'),
    url(r'^feeds/', include('feeds.urls')),
    url(r'^groups/', include('groups.urls')),
    url(r'^messages/', include('messenger.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^notifications/$', activities_views.notifications,
        name='notifications'),
    url(r'^notifications/last/$', activities_views.last_notifications,
        name='last_notifications'),
    url(r'^notifications/check/$', activities_views.check_notifications,
        name='check_notifications'),
    url(r'^search/$', search_views.search, name='search'),
    url(r'^(?P<username>[^/]+)/$', core_views.profile, name='profile'),
    url(r'^i18n/', include('django.conf.urls.i18n', namespace='i18n')),
    url(r'^jsi18n/(?P<packages>\S+?)/$',django.views.i18n.javascript_catalog),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
