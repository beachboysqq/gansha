# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from ragendja.urlsauto import urlpatterns
#from ragendja.auth.urls import urlpatterns as auth_patterns
from django.contrib import admin

admin.autodiscover()

handler500 = 'ragendja.views.server_error'

#urlpatterns = auth_patterns + patterns('',
#    ('^admin/(.*)', admin.site.root),
#)

urlpatterns = patterns('',
                       ('^admin/(.*)', admin.site.root)
                       )
urlpatterns += patterns('userAdmin.views',
                       (r'^$','index'),
                       (r'^(home)/$','home'),
                       (r'^(myhome)/$','home'),
                       (r'^myinfo/$', 'myinfo'),
                       (r'^editmyinfo/$', 'editmyinfo'),
                       (r'^search/$','search'),
                       (r'^friends/$', 'friends'),
                       (r'^addfriend/$', 'addfriend'),
                       (r'^removefriend/$','removefriend'),
                       (r'^acceptfriend/$','acceptfriend'),
                       (r'^deny/$','deny'),
                       (r'^test/','test'),
)

urlpatterns += patterns('event.views',
                        (r'^event/$','event'),
                        (r'^addevent/$','add_event'),
                        (r'^del_event/$','del_event'), 
                        (r'^editevent/$','edit_event'),
                        (r'^add_sub_event/$','add_sub_event'),
                        (r'^edit_sub_event/$','edit_sub_event'),
                        (r'^del_sub_event/$','del_sub_event'),
                        (r'^done_sub_event/$','done_sub_event'),
                        (r'^add_to_concern/$','add_to_concern'),
                        (r'^remove_concern/$','remove_concern'),
                        (r'^doing/$','events_doing'),
                        (r'^todo/$','events_todo'),
                        (r'^done/$','events_done'),
                        # (r'^admin/', include('django.contrib.admin.urls')),
)

urlpatterns += patterns('blog.views',
                        (r'^blog/$','blog'), 
                        (r'^addblog/$','add_blog'), 
                        (r'^editblog/$','edit_blog'),
                        (r'^delblog/$','del_blog'),
                        (r'^add_comment/$','add_comment'),                
                        (r'^del_comment/$','del_comment'),                
                        (r'^message/$','message'),                
                        (r'^add_mes/$','add_mes'),                
                        (r'^del_mes/$','del_mes'),                
                        )
