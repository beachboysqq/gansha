from django.contrib import admin
from gansha.blog.models import *

#class BlogAdmin(admin.ModelAdmin):
#    list_display=('id','author','title','publish_time')


class CommentAdmin(admin.ModelAdmin):
    list_display=('id','author','blog_id','publish_time')

class MesAdmin(admin.ModelAdmin):
    list_display=('id','sender','receiver','content','publish_time')
    
#admin.site.register( Blog,BlogAdmin )
admin.site.register( Comment,CommentAdmin )
admin.site.register( Mes,MesAdmin )
