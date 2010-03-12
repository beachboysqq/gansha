#coding=utf-8
from google.appengine.ext import db
from google.appengine.api import users
import datetime

class Event( db.Model ):
    title = db.StringProperty()
    desc = db.TextProperty()
    is_public = db.BooleanProperty( default=True )
    progress = db.IntegerProperty( default=0 )
    is_done = db.BooleanProperty( default=False )
    publish_date = db.DateProperty( auto_now_add=True )
    start_date = db.DateProperty( default=datetime.date(4000,1,1) )
    end_date = db.DateProperty( default=datetime.date(1900,1,1) )
    num_se = db.IntegerProperty( default=0 )

    
class Subevent( db.Model ):
    event = db.ReferenceProperty( Event )
    content = db.StringProperty()
    start_date = db.DateProperty()
    end_date = db.DateProperty()
    is_done = db.BooleanProperty( default=False )
    isexpired = db.BooleanProperty( default=False )

class History( db.Model ):
    event = db.ReferenceProperty( Event )
    publish_time = db.DateTimeProperty( auto_now_add=True )
    
    content = db.StringProperty()    
