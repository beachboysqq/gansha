from django.forms import ModelForm
from gansha.blog.models import *

class BlogForm( ModelForm ):
    class Meta:
        model = Blog
        exclude = ('author','event_id','publish_time')

class CommentForm( ModelForm ):
    class Meta:
        model = Comment
        exclude = ('author','blog_id','publish_time')

class MesForm( ModelForm ):
    class Meta:
        model = Mes

