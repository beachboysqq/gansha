#coding=utf-8
from django.contrib import admin
from models import *

class eventAdmin(admin.ModelAdmin):    
    list_display = ('user','title','publish_date' )
    fields = ('user','title','desc','is_public','progress','is_done',
              'publish_date','start_date','end_date','num_se')

admin.site.register(Event,eventAdmin)

class seAdmin(admin.ModelAdmin):    
    list_display = ('content','start_date' )

admin.site.register(Subevent,seAdmin)
