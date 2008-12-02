# -*- coding: cp936 -*-
from django.db import models
from django import forms
from django.contrib.auth.models import User
#这里用了User表的相关信息，操作时有什么不明白，直接看原文件，在你装Django的django.contrib.auth.models目录下。

class UserProfile(models.Model):#此表没你们什么事，仅在注册验证时有用
    username = models.OneToOneField(User)
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()

    class Meta:
        db_table = "UserProfile"

class UserBasicInfo(models.Model):
    GENDER_CHOICES =(
                        ('M', 'Male'),
                        ('F', 'Female'),
                    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES,default="M")
    username = models.OneToOneField(User)
    #gender = models.BooleanField(default=True)#性别
    headshot = models.ImageField(upload_to='photos/%Y/%m/%d',blank=True)#头像
    #integeral = models.IntegerField(default=10)#积分
    achievement = models.IntegerField(default=0)#成就指数
    graduate_school = models.CharField(max_length=30,blank=True)#毕业学校
    location = models.CharField(max_length=30,blank=True)#住处
    signature = models.CharField(max_length=50,blank=True)

    def __unicode__(self):
        return u'%s' % self.email

    class Meta:
        db_table = "UserBasicInfo"

class ContactInfo(models.Model):
    username = models.OneToOneField(User)
    qq = models.CharField(max_length =15,blank=True)
    msn = models.CharField(max_length =75,blank=True)
    personal_site=models.URLField(verify_exists=True, max_length=200,blank=True) 

    class Meta:
        db_table ="ContactInfo"

class UserForm(forms.ModelForm):
    class Meta:
        model =User;

class Friends(models.Model):
    username = models.OneToOneField(User,related_name="user")
    friend_name = models.OneToOneField(User,related_name="friend_user")

    class Meta:
        db_table ="Friends"
