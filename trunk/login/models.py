# -*- coding: utf-8 -*-
from google.appengine.ext import db
from google.appengine.api import users
from django.contrib.auth.models import User

class User_profile( db.Model ):
    user = db.UserProperty()
    uid = db.StringProperty()
    uname = db.StringProperty()
    age = db.IntegerProperty()
    headshot = db.StringProperty()
    sign = db.StringProperty()
    last_login = db.DateTimeProperty()
    gender = db.StringProperty( choices=set(['male','female','unkown']),default='unkown' )
    is_public = db.BooleanProperty( default=True )
    addr = db.StringProperty()
    rank = db.IntegerProperty( default=0 )
    blog = db.StringProperty()
    job = db.StringProperty()
    other = db.StringProperty()

class Friends( db.Model ):
    user = db.UserProperty()
    myfriend = db.UserProperty()

class FriendRequest( db.Model ):
    sender = db.UserProperty()
    receiver = db.UserProperty()
    message = db.StringProperty()

