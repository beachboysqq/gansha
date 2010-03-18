# -*- coding: utf-8 -*-
from google.appengine.ext import db
from google.appengine.api import users
from event.models import Event
import datetime

class Blog( db.Model ):
    event = db.ReferenceProperty( Event,required=False )
    title = db.StringProperty()
    content = db.TextProperty()
    is_public = db.BooleanProperty( default=True )
    publish_time = db.DateTimeProperty()

class Tag( db.Model ):
    word = db.StringProperty( default='' )
    num = db.IntegerProperty( default=0 )

class BlogTag( db.Model ):
    blog = db.ReferenceProperty( Blog )
    tag = db.ReferenceProperty( Tag )

class Comment( db.Model ):
    sender = db.UserProperty()
    blog = db.ReferenceProperty( Blog )
    content = db.TextProperty()
    publish_time = db.DateTimeProperty()
    
class Mes( db.Model ):
    sender = db.UserProperty( required=True )
    content = db.StringProperty( required=True ) 
    publish_time = db.DateTimeProperty()
    
    
