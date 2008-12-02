# -*- coding: cp936 -*-
from django.db import models
from django import forms
from django.contrib.auth.models import User
#��������User��������Ϣ������ʱ��ʲô�����ף�ֱ�ӿ�ԭ�ļ�������װDjango��django.contrib.auth.modelsĿ¼�¡�

class UserProfile(models.Model):#�˱�û����ʲô�£�����ע����֤ʱ����
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
    #gender = models.BooleanField(default=True)#�Ա�
    headshot = models.ImageField(upload_to='photos/%Y/%m/%d',blank=True)#ͷ��
    #integeral = models.IntegerField(default=10)#����
    achievement = models.IntegerField(default=0)#�ɾ�ָ��
    graduate_school = models.CharField(max_length=30,blank=True)#��ҵѧУ
    location = models.CharField(max_length=30,blank=True)#ס��
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
