# -*- coding: utf-8 -*-
from google.appengine.ext import db
from google.appengine.api import users
from event.models import Event
from search.core import SearchIndexProperty,porter_stemmer
import datetime

class Blog( db.Model ):
    author = db.UserProperty()
    event = db.ReferenceProperty( Event )
    title = db.StringProperty()
    content = db.TextProperty()
    publish_time = db.DateTimeProperty( auto_now_add=True )
    
    search_index = SearchIndexProperty( ('title','content'),indexer=porter_stemmer,relation_index=False ) 

class Comment( db.Model ):
    receiver = db.UserProperty()
    sender = db.UserProperty()
    blog = db.ReferenceProperty( Blog )
    content = db.TextProperty()
    publish_time = db.DateTimeProperty( auto_now_add=True )
    
class Mes( db.Model ):
    sender = db.UserProperty( required=True )
    receiver = db.UserProperty( required=True )
    content = db.StringProperty( required=True ) 
    publish_time = db.DateTimeProperty( auto_now_add=True )
    
