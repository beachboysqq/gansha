# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from ragendja.urlsauto import urlpatterns
from ragendja.auth.urls import urlpatterns as auth_patterns
#from django.contrib import admin
from django.conf.urls.defaults import *
from django.conf import settings
#admin.autodiscover()

handler500 = 'ragendja.views.server_error'

#urlpatterns = auth_patterns + patterns('',
#                                       ('^admin/(.*)', admin.site.root),
#) + urlpatterns

urlpatterns += patterns('django.views.generic.simple',
                        (r'^about/$',             'direct_to_template', {'template': 'about.htm'}),
                        (r'^contact/$', 'direct_to_template', {'template': 'contact.htm'}),
                        (r'^log/$', 'direct_to_template', {'template': 'dev_log.htm'}),
)

urlpatterns += patterns('login.views',
                        (r'^$','index'),
                        (r'^login/$','login'),
                        (r'^export/$','export_data'),
                        (r'^import/$','import_data'),
                        (r'^repair/$','repair_tags'),
)

urlpatterns += patterns('blog.views',
                        (r'^blogview/$','blogview'),
                        (r'^blog/$','blog'), 
                        (r'^addblog/$','add_blog'), 
                        (r'^editblog/$','edit_blog'),
                        (r'^delblog/$','del_blog'),
                        (r'^add_comment/$','add_comment'),                
                        (r'^del_comment/$','del_comment'),                
                        (r'^message/$','message'),                
                        (r'^add_mes/$','add_mes'),                
                        (r'^del_mes/$','del_mes'),                
                        (r'^note/$','note'),                
                        (r'^add_note/$','add_note'),                
                        (r'^del_note/$','del_note'),                
                        )

urlpatterns += patterns('event.views',
                        (r'^home/$','home'),
                        (r'^event/$','event'),
                        (r'^addevent/$','add_event'),
                        (r'^del_event/$','del_event'), 
                        (r'^editevent/$','edit_event'),
                        (r'^add_sub_event/$','add_sub_event'),
                        (r'^edit_sub_event/$','edit_sub_event'),
                        (r'^del_sub_event/$','del_sub_event'),
                        (r'^done_sub_event/$','done_sub_event'),
                        (r'^events/$','events_list'),
                        (r'^doing/$','events_doing'),
                        (r'^todo/$','events_todo'),
                        (r'^done/$','events_done'),
                        # (r'^admin/', include('django.contrib.admin.urls')),
)

urlpatterns += patterns('tip.views',
                        (r'^addtip/$','add_tip'),
                        (r'^deltip/$','del_tip'),
                        (r'^tips/$','tips'),
)
