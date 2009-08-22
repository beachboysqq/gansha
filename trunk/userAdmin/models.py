# -*- coding: utf-8 -*-
from google.appengine.ext import db
from google.appengine.api import users
from search.core import SearchIndexProperty, porter_stemmer

class User_profile( db.Model ):
    user = db.UserProperty()
    age = db.IntegerProperty()
    headshot = db.StringProperty()
    sign = db.StringProperty()
    last_login = db.DateProperty()
    gender = db.StringProperty( choices=set(['male','female','unkown']),default='unkown' )
    is_public = db.BooleanProperty( default=True )
    addr = db.StringProperty()
    rank = db.IntegerProperty( default=0 )
    blog = db.StringProperty()
    job = db.StringProperty()
    other = db.StringProperty()

    #search_index = SearchIndexProperty( ('title','desc'),indexer=porter_stemmer )

class Friends( db.Model ):
    user = db.UserProperty()
    myfriend = db.UserProperty()

class FriendRequest( db.Model ):
    sender = db.UserProperty()
    receiver = db.UserProperty()
    message = db.StringProperty()

