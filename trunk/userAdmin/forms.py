# -*- coding: cp936 -*-
from django.contrib.auth.models import User
from django import forms

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=30)
    email = forms.EmailField()
    password1= forms.CharField(max_length=20,widget=forms.PasswordInput,min_length=6)
    password2= forms.CharField(max_length=20,widget=forms.PasswordInput,min_length=6 )
    
    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username =username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError("Username already exists.")
    
    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User.objects.get(email = email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError("Email address already exists.")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data.get("password2", "")
        if password1 != password2:
            raise forms.ValidationError("The two password fields didn't match.")
        return password2

    def save(self):
        u= User.objects.create_user(self.cleaned_data['username'],
                                    self.cleaned_data['email'],
                                    self.cleaned_data['password2'],)
        #u= User.objects.create_user(self.cleaned_data['username'],
        #                            self.cleaned_data['email'],)
        u.is_active =False
        u.save()
        return u

class ChangePasswordForm(forms.Form):
    username = forms.CharField(max_length=30)
    password_old= forms.CharField(max_length=20,widget=forms.PasswordInput,min_length=6 )
    password1= forms.CharField(max_length=20,widget=forms.PasswordInput,min_length=6 )
    password2= forms.CharField(max_length=20,widget=forms.PasswordInput,min_length=6 )

    def clean_password_old(self):
        name = self.cleaned_data["username"]
        password =self.cleaned_data.get("password_old", "")
        user=User.objects.get(username =name)
        if not user.check_password(password):
            raise forms.ValidationError("old password does not right!")
        
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data.get("password2", "")
        if password1 != password2:
            raise forms.ValidationError("The two password fields didn't match.")
        return password2

class LoginForm(forms.Form):
    username = forms.CharField(max_length=30)
    password= forms.CharField(max_length=128,widget=forms.PasswordInput)

class EditInfoForm(forms.Form):
    GENDER_CHOICES =(
                        ('M', 'Male'),
                        ('F', 'Female'),
                    )
    headshot = forms.ImageField(required=False,error_messages={'invalid_image':'A invalid image!'})
    graduate_school = forms.CharField(max_length=30,required=False)
    location = forms.CharField(max_length=30,required=False)
    qq = forms.CharField(max_length =15,required=False)
    msn = forms.CharField(max_length =75,required=False)
    signature = forms.CharField(max_length=50,widget=forms.Textarea,required=False)
    personal_site=forms.URLField(verify_exists=True, max_length=200,required=False)
    gender = forms.CharField(max_length=1,widget=forms.Select(choices=GENDER_CHOICES))
    
    
        



