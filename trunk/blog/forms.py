# -*- coding: cp936 -*-
#from gansha.blog.models import *
from django import forms

from django.db import models
import datetime
from django.forms import ModelForm


#blogissue.htm
class EditBlogForm(forms.Form):
    post_type=forms.CharField(required=True,max_length=10)
    event_id=forms.CharField(required=False,max_length=10)
    blog_info=forms.CharField(required=False,max_length=10)
    title=forms.CharField(required=True,max_length=100)#,error_message=_("标题不能太长！"))
    content=forms.CharField(required=True,widget=forms.Textarea(attrs={'rows': 15, 'cols': 58}))#error_message=_("内容不能为空！"))
        
#blogdetail.htm,编辑、删除blog使用
class BlogInfo(forms.Form):
    blog_info=forms.CharField(required=True,max_length=10)
    event_info=forms.CharField(required=False,max_length=10)
    
#blogdetail.htm,编辑comment使用
class EditRemarkForm(forms.Form):
    blog_id=forms.CharField(required=True,max_length=10)
    event_id=forms.CharField(required=False,max_length=10)
    new_content=forms.CharField(required=True,widget=forms.Textarea(attrs={'rows':5,'cols':65}))
    
#blogdetail.htm,删除comment使用
class DelCommentInfo(forms.Form):
    blog_id_info=forms.CharField(required=True,max_length=10)
    event_id_info=forms.CharField(required=False,max_length=10)
    comment_id_info=forms.CharField(required=True,max_length=10)
    
