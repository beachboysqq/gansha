from appengine_django.models import BaseModel
from google.appengine.ext import db
from google.appengine.api import users
import datetime

class Event( BaseModel ):
    user = db.UserProperty()
    title = db.StringProperty()
    desc = db.StringProperty(multiline=True)
    is_public = db.BooleanProperty(default=True)
    progress = db.IntegerProperty(default=0)
    is_done = db.BooleanProperty(default=False)
    publish_date = db.DateProperty( auto_now_add=True )
    start_date = db.DateProperty( default=datetime.date(4000,1,1) )
    end_date = db.DateProperty( default=datetime.date(1000,1,1) )
    num_se = db.IntegerProperty( default=0 )

class Sub_event( BaseModel ):
    user = db.UserProperty()
    event = db.ReferenceProperty( Event )
    content = db.StringProperty(required=True)
    start_date = db.DateProperty()
    end_date = db.DateProperty()
    is_done = db.BooleanProperty( default=False )
    isexpired = db.BooleanProperty( default=False )

class History( BaseModel ):
    user = db.UserProperty()
    event = db.ReferenceProperty( Event )
    date = db.DateProperty( auto_now_add=True )
    content = db.StringProperty() 

class Concern( db.Model ):
    user = db.UserProperty()
    event = db.ReferenceProperty( Event,collection_name="my_event" )
    c_event = db.ReferenceProperty( Event,collection_name="concern_event" )
   
