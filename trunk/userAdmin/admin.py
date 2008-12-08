from django.contrib import admin
from django.contrib.auth.models import User
from gansha.userAdmin.models import UserBasicInfo,ContactInfo

class UserAdmin(admin.ModelAdmin):
    list_display=('username','gender','headshot','achievement','graduate_school','location')
    
class ContactAdmin(admin.ModelAdmin):
    list_display=('username','qq','msn','personal_site')
    
admin.site.register(UserBasicInfo,UserAdmin)
admin.site.register(ContactInfo,ContactAdmin)