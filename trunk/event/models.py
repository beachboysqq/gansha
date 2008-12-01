from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Event( models.Model ):
    title=models.CharField( max_length=255 )
    description=models.TextField( blank=True )
    isprivacy=models.NullBooleanField( default=False )
    progress=models.FloatField()
    publish_date=models.DateField( auto_now_add=True )
    user_id=models.ForeignKey( User )
    
    def __unicode__(self):
        return self.title
    
class Sub_event( models.Model ):
    content=models.CharField( max_length=255 )
    start_date=models.DateField()
    end_date=models.DateField()
    isdone=models.NullBooleanField()
    enent_id=models.ForeignKey( Event )
    
    def __unicode__(self):
        return self.title
