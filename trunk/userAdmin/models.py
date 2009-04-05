from appengine_django.models import BaseModel
from google.appengine.ext import db
from google.appengine.api import users

class User_profile(BaseModel):
    user = db.UserProperty()
    age = db.IntegerProperty()
    headshot = db.BlobProperty()
    sign = db.StringProperty()
    last_login = db.DateProperty()
    gender = db.StringProperty(choices=set(['male','female','unkown']),default='unkown')
    is_public = db.BooleanProperty(default=True)
    addr = db.StringProperty()
    rank = db.IntegerProperty(default=0)
    blog = db.StringProperty()
    job = db.StringProperty()
    other = db.StringProperty()

class Friends(BaseModel):
    user = db.UserProperty()
    myfriend = db.UserProperty()

class FriendRequest(BaseModel):
    sender = db.UserProperty()
    receiver = db.UserProperty()
    message = db.StringProperty()

