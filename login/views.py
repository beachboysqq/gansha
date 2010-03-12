#coding=utf-8
from google.appengine.api import users
from django.http import HttpResponseRedirect

#not admin,go to blogview,else go to home
def index(request):
    user = users.get_current_user()
    if not user or not users.is_current_user_admin():
        return HttpResponseRedirect('/blogview')
    else:
        return HttpResponseRedirect('/home')

def login(request):
    user = users.get_current_user()
    if not user:
        loginurl = users.create_login_url('/')
        return HttpResponseRedirect(loginurl)
    else:
        return HttpResponseRedirect('/')

