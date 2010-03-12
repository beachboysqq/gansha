#coding=utf-8
from django.contrib import admin
from models import *

class userAdmin(admin.ModelAdmin):    
    list_display = ('uid','last_login','gender','rank','job' )
    
admin.site.register(User_profile,userAdmin)

