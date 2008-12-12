# -*- coding: cp936 -*-
from django.db import models
from django.contrib.auth.models import User
import datetime

#chief event you want to do
class Event( models.Model ):
    user_id = models.ForeignKey( User )
    title = models.CharField( max_length=255 )
    description = models.TextField( blank=True )
    isprivacy = models.BooleanField( default=False )
    progress = models.IntegerField( default=0 )
    publish_date = models.DateField( auto_now=True )
    start_date = models.DateField( default=datetime.date(4000,1,1) )
    end_date = models.DateField(default=datetime.date(1000,1,1) )
    num_se = models.IntegerField( default=0 )
    
    def __unicode__(self):
        return self.title

#set the chief event into several targets
class Sub_event( models.Model ):
    event_id=models.ForeignKey( Event )
    content=models.CharField( max_length=255 )
    start_date=models.DateField()
    end_date=models.DateField()
    isdone=models.BooleanField( default=False )
    isexpired = models.BooleanField( default=False )
    
    def __unicode__(self):
        return self.title

#just record the sub event you done,and when
class History( models.Model ):
    user_id = models.ForeignKey( User )
    event_id = models.ForeignKey( Event )
    date = models.DateField( auto_now=True )
    content = models.CharField( max_length=255 ) 
    def __unicode__( self ):
        return self.content
   
class Concern( models.Model ):
    user_id = models.ForeignKey( User )
    event_id = models.ForeignKey( Event )
    ce_id = models.ForeignKey( Event,related_name="concern_event" )
   
