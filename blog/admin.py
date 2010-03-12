#coding=utf-8
from django.contrib import admin
from models import *

class blogAdmin(admin.ModelAdmin):    
    list_display = ('title','publish_time' )
    fields = ('event','title','publish_time')

admin.site.register(Blog,blogAdmin)
admin.site.register(Comment)
