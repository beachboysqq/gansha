# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from google.appengine.ext import db

class Tip( db.Model ):
    content = db.StringProperty()    
    publish_time = db.DateTimeProperty( auto_now_add=True )
    


