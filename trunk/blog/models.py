# -*- coding: cp936 -*-
from django.db import models
from gansha.event.models import Event
from django.contrib.auth.models import User

class Blog( models.Model ):
    author = models.ForeignKey( User )
    event_id = models.ForeignKey( Event )
    title = models.CharField( max_length=255 )
    content = models.TextField()
    publish_time = models.DateTimeField( auto_now=True )
    
    def __unicode__(self):
        return self.title

class Comment( models.Model ):
    author = models.ForeignKey( User )
    blog_id = models.ForeignKey( Blog )
    content = models.TextField()
    publish_time = models.DateTimeField( auto_now=True )
    
    def __unicode__(self):
        return self.content

#leave message
class Mes( models.Model ):
    sender = models.ForeignKey( User,related_name="senders" )
    receiver = models.ForeignKey( User,related_name="rceivers" )
    content = models.CharField( max_length=1000 ) 
    publish_time = models.DateTimeField( auto_now=True )
    
    def __unicode__( self ):
        return self.content
   
