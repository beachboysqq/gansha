from django.db import models
from django import forms
from django.contrib.auth.models import User
from gansha.event.models import Event
import datetime


class Blog(models.Model):
    
    #event_id = models.ForeignKey(Event)
    title = models.CharField(max_length=100,default='Default Title')
    content = models.TextField()
    publish_time = models.DateTimeField(default=datetime.datetime.now)
    user_id = models.ForeignKey(User)
    class Meta:
        db_table ="Blog"

class Remark(models.Model):
    blog_id = models.ForeignKey(Blog)
    content = models.TextField()
    publish_time = models.DateTimeField(default=datetime.datetime.now)
    remarker_id = models.ForeignKey(User)

    class Meta:
        db_table ="Remark"
