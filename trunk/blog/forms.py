# -*- coding: cp936 -*-
from django.contrib.auth.models import User
from django import forms
from gansha.blog.models import *
from django.db import models
import datetime
from django.forms import ModelForm

class EditBlogForm(ModelForm):
    #title = forms.CharField(required = True,max_length=100)#,error_message=_("标题不能太长！"))
    #content = forms.TextField(required = True)#error_message=_("内容不能为空！"))
    class Meta:
        model=Blog
        exclude=('user_id','publish_time')
       # exclude=('user_id','publish_time','event_id')
        




class EditRemarkForm(ModelForm):
    class Meta:
        model=Remark
        exclude=('blog_id','publish_time','remarker_id')
