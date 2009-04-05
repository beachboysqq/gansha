from appengine_django.models import BaseModel
from google.appengine.ext import db
from google.appengine.api import users
from event.models import Event
import datetime

class Blog( BaseModel ):
    author = db.UserProperty()
    event = db.ReferenceProperty(Event)
    title = db.StringProperty()
    content = db.TextProperty()
    publish_time = db.DateTimeProperty( auto_now_add=True )

class Comment( BaseModel ):
    receiver = db.UserProperty()
    sender = db.UserProperty()
    blog = db.ReferenceProperty( Blog )
    content = db.TextProperty()
    publish_time = db.DateTimeProperty( auto_now_add=True )
    
class Mes( BaseModel ):
    sender = db.UserProperty()
    receiver = db.UserProperty()
    content = db.StringProperty() 
    publish_time = db.DateTimeProperty( auto_now_add=True )
    
