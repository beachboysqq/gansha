# -*- coding: cp936 -*-
from django.forms import ModelForm
from gansha.blog.models import *
from django import forms

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

#blogissue.htm
class EditBlogForm(forms.Form):
    event_id=forms.CharField(required=False,max_length=10)
    blog_info=forms.CharField(required=False,max_length=10)
    title=forms.CharField(required=True,max_length=100)#,error_message=_(""))
    content=forms.CharField(required=True,widget=forms.Textarea(attrs={'rows': 60, 'cols': 60}))#error_message=_("内容不能为空！"))
        
#blogdetail.htm
class BlogInfo(forms.Form):
    blog=forms.CharField(required=True,max_length=10)
    event_info=forms.CharField(required=False,max_length=10)
    com_id = forms.CharField(required = False,max_length=10)
    
#blogdetail.htm
class EditComForm(forms.Form):
    blog_id=forms.CharField(required=True,max_length=10)
    event_id=forms.CharField(required=False,max_length=10)
    new_content=forms.CharField(required=True,widget=forms.Textarea(attrs={'rows':15,'cols':65}))
    
    
