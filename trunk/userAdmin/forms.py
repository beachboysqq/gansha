from google.appengine.ext.db import djangoforms
from userAdmin.models import User_profile

class MyinfoForm(djangoforms.ModelForm):
    class meta:
        model = User_profile
        exclude = ['user','last_login','rank']
