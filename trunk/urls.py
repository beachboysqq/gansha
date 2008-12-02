from django.conf.urls.defaults import *
from django.contrib import admin
from gansha.event.views import test
from gansha.userAdmin.views import *
from django.conf import settings

admin.autodiscover()
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^gansha/', include('gansha.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/(.*)', admin.site.root),
    (r'^$',index),
    ('^admin/(.*)', admin.site.root),
    (r'^register/$',register),
    (r'^home/$',home),
    (r'^confirm/(\w+)$',confirm),
    (r'^home/$', home),
    (r'^home/myinfo/$', myinfo),
    (r'^home/editmyinfo/$', editmyinfo),
    (r'^home/changepassword/$', changepassword),
    (r'^home/logout/$', logout),
    #(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'D:/static', 'show_indexes': True}),
)

