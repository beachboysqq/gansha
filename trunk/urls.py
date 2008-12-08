from django.conf.urls.defaults import *
from django.contrib import admin
from gansha.userAdmin.views import *
from gansha.event.views import *
from django.conf import settings

admin.autodiscover()
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
#    (r'^gansha/', include('gansha.foo.urls')), 
    (r'^test/', test),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    ('^admin/(.*)', admin.site.root),
    (r'^$',index),
    (r'^register/$',register),
    (r'^search/', search),
    (r'^home/$',home),
    (r'^confirm/(\w+)$',confirm),
    (r'^home/$', home),
    (r'^myinfo/$', myinfo),
    (r'^editmyinfo/$', editmyinfo),
    (r'^changepassword/$', changepassword),
    (r'^friends/$', friends),
    (r'^addfriend/$', addfriend),
    (r'^removefriend/$',removefriend),
    (r'^acceptfriend/$',acceptfriend),
    (r'^deny/$',deny),
    (r'^logout/$', logout),
    (r'^addevent/$',add_event), 
    (r'^editevent/$',edit_event),
    (r'^event/$',event),
    (r'^add_sub_event/$',add_sub_event),
    (r'^edit_sub_event/$',edit_sub_event),
    (r'^del_sub_event/$',del_sub_event),
    (r'^done_sub_event/$',done_sub_event),
    (r'^doing/$',events_doing),
    (r'^todo/$',events_todo),
    (r'^done/$',events_done),
    #(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'D:/static', 'show_indexes': True}),
)

