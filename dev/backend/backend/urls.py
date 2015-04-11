from django.conf.urls.static import static
from django.conf.urls import patterns, include, url
from django.contrib import admin
from backend import settings

urlpatterns = patterns('rest.router',
    # Examples:
    url(r'^bannedhashes/$', 'bannedhashList'),
    url(r'^roles/$', 'rolesList'),
    url(r'^files/$', 'filesList'),
    url(r'^files/subject/(?P<pk>[0-9]+)/$', 'fileListSubject'),
    url(r'^admin/', include(admin.site.urls)),


    # APIs
    # System
    url(r'^signup/$', 'signup'),
    url(r'^confirm_email/(?P<cookie>.*)/$', 'confirmEmail'),
    url(r'^login/$', 'login'),
    url(r'^logout/$', 'logout'),
    url(r'^recover_password/$', 'recoverPassword'),

    # User
    url(r'^user/$', 'user'),
    url(r'^user/subjects/$', 'user_subjects'),
    url(r'^user/(?P<pk>[0-9]+)/$', 'userById'),
    url(r'^users/rol/(?P<pk>[0-9]+)/$', 'usersByRol'),

    # Notes
    url(r'^note/level/(?P<level>[0-9]+)/$', 'noteByLevel'),
    url(r'^note/(?P<pk>[0-9]+)/$', 'noteById'),
    url(r'^note/$', 'note'),

    # Calendar
    url(r'^calendar/(?P<period>(month|day))/(?P<initDate>([0-9]|-)*)/$', 'calendarByPeriod'),
    url(r'^calendar/(?P<pk>[0-9]+)/$', 'calendarById'),
    url(r'^calendar/$', 'calendar'),

    # Files
    url(r'^file/$', 'file'),
    url(r'^file/f/(?P<pk>[0-9]+)/$', 'fileBinary'),
    url(r'^file/(?P<pk>[0-9]+)/$', 'fileById'),

    #SubjectsTree
    url(r'^subjectsTree/$', 'subjectsTree'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
