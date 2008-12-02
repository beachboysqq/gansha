from gansha.userAdmin.models import UserForm
from django.http import HttpResponse
from django.http import HttpResponseRedirect

import datetime, random, sha
from django.shortcuts import render_to_response, get_object_or_404
from django.core.mail import send_mail
from gansha.userAdmin.models import UserProfile,UserBasicInfo,ContactInfo
from gansha.userAdmin.forms import RegistrationForm,LoginForm,EditInfoForm,ChangePasswordForm
from django.contrib.auth.models import User
from django.template import Context, Template

def register(request):
    if request.user.is_authenticated():
        # They already have an account, don't let them register again
        return HttpResponse('member')
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Save the user 
            new_user = form.save()
            
            # Build the activation key for their account                                                                   
            salt = sha.new(str(random.random())).hexdigest()[:5]
            activation_key = sha.new(salt+new_user.username).hexdigest()
            key_expires = datetime.datetime.today() + datetime.timedelta(2)
            
            # Create and save their profile
            new_profile = UserProfile(username=new_user,
                                      activation_key=activation_key,
                                      key_expires=key_expires)
            new_profile.save()
            
            # Send an email with the confirmation link
            email_subject = 'Your new example.com account confirmation'
            email_body = "Hello, %s, and thanks for signing up for an example.com account!\n\nTo activate your account, click this link within 48 hours:\n\nhttp://localhost/confirm/%s" % (
                        new_user.username,
                        new_profile.activation_key)
            send_mail(email_subject,
                      email_body,
                      'l0he1g@163.com',
                      [new_user.email])
            
            return render_to_response('register.htm', {'created': True,'email':new_user.email})
    else:
        form = RegistrationForm()
    return render_to_response('register.htm', {'form': form})

def confirm(request, activation_key):
    if request.user.is_authenticated():
        #return render_to_response('confirm.htm', {'has_account': True})
        return HttpResponse('member')
    user_profile = get_object_or_404(UserProfile,
                                     activation_key=activation_key)
    if user_profile.key_expires < datetime.datetime(1970,1,2):
        return render_to_response('confirm.htm', {'confirmed': True,'expired': False})#confirmation have been done
    if user_profile.key_expires < datetime.datetime.today():
        return render_to_response('confirm.htm', {'expired': True})
        #return HttpResponse('expire')
    user_account = user_profile.username
    #user_account = User.objects.get(id=user_profile.username_id)
    user_account.is_active = True
    user_account.save()
    user_profile.key_expires= datetime.date(1970,1,1)#there is no second time of confirmation
    user_profile.save()
    basicInfo = UserBasicInfo()
    basicInfo.username= user_profile.username
    basicInfo.save()
    contactInfo = ContactInfo()
    contactInfo.username= user_profile.username
    contactInfo.save()
    
    request.session['member_id']=user_account.id#for redirect in 20 seconds
    return render_to_response('confirm.htm', {'success': True})
    #return HttpResponse('confirm success')

        #if request.user.is_authenticated():
        # They already have an account; don't let them register again
        #return HttpResponse('member')
    if request.method=='POST':
        form = LoginForm(request.POST)
        try:
            m = User.objects.get(username=request.POST['username'])
            if not m.is_active:
                return render_to_response('index.htm', {'form': form,'login':False,'activated':False})
        except User.DoesNotExist:
            return render_to_response('index.htm', {'form': form,'login':False,'match':False})
        #session['member_id'need to be checked ,wait
        if m.check_password(request.POST['password']):
            request.session['member_id'] = m.id
            #id=request.session['member_id']
            user = User.objects.get(id = m.id)
            username = user.username
            last_login = user.last_login
            #basicInfo = UserBasicInfo.objects.filter(username = id)
            basicInfo = user.userbasicinfo
            achievement = basicInfo.achievement
            signature = basicInfo.signature
            c = Context({"username":username,
                         "achievement":achievement,
                         "signature":signature,
                         "last_login":last_login,})
            return render_to_response('home.htm', c)
        else:
            return render_to_response('index.htm', {'form': form,'login':False,'match':False})
    else:
        form = LoginForm()
    return render_to_response('index.htm', {'form': form})

def index(request):
    #user has been logined,
    #improve1:session doesn't work...
    #improve2:after flush,the error info maitain!
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        uname=request.POST['username']
        if form.is_valid():
            try:
                m = User.objects.get(username=uname)
                if not m.is_active:
                    return render_to_response('index.htm', {'form': form,'error':'Account has not been actived!'})
            except User.DoesNotExist:
                return render_to_response('index.htm', {'form':form,'error':'User not exsit!'})
            
            if m.check_password(request.POST['password']):
                request.session['member_id'] = m.id
                return HttpResponseRedirect('home/')
            else:
                return render_to_response('index.htm', {'form': form,'error':'Wrong password!','username':uname})
    else:
        form = LoginForm()
    return render_to_response('index.htm', {'form':form,'error':''})

def home(request):
    try:
        id =request.session['member_id']
    except KeyError:
        return HttpResponse('You have not login,and have no right of accessing!')
    logined =True
    
    user = User.objects.get(id = id)
    username = user.username
    last_login = user.last_login
            #basicInfo = UserBasicInfo.objects.filter(username = id)
    basicInfo = user.userbasicinfo
    achievement = basicInfo.achievement
    signature = basicInfo.signature
    c = Context({"username":username,
                "achievement":achievement,
                "signature":signature,
                "last_login":last_login,'logined':logined})
    return render_to_response('home.htm', c)

def myinfo(request):
    try:
        id =request.session['member_id']
    except KeyError:
        return HttpResponse('You have not login,and have no right of accessing!')
    logined =True
    
    user = User.objects.get(id = id)
    username = user.username
    last_login = user.last_login
            #basicInfo = UserBasicInfo.objects.filter(username = id)
    basicInfo = user.userbasicinfo
    achievement = basicInfo.achievement
    signature = basicInfo.signature
    gender = basicInfo.gender
    graduate_school = basicInfo.graduate_school
    location = basicInfo.location

    contactInfo = user.contactinfo
    qq = contactInfo.qq
    msn = contactInfo.msn
    
    c = Context({"username":username,
                "achievement":achievement,
                "signature":signature,
                "last_login":last_login,
                'logined':logined,
                "gender":gender,
                "graduate_school":graduate_school,
                "location":location,
                "qq":qq,
                'msn':msn})
    return render_to_response('myinfo.htm', c)

def editmyinfo(request):
    try:
        id =request.session['member_id']
    except KeyError:
        return HttpResponse('You have not login,and have no right of accessing!')
    logined =True
    
    user = User.objects.get(id = id)
    username = user.username
    last_login = user.last_login
            #basicInfo = UserBasicInfo.objects.filter(username = id)
    basicInfo = user.userbasicinfo
    achievement = basicInfo.achievement
    signature = basicInfo.signature
    gender = basicInfo.gender
    graduate_school = basicInfo.graduate_school
    location = basicInfo.location

    contactInfo = user.contactinfo
    qq = contactInfo.qq
    msn = contactInfo.msn

    if request.POST:
        form = EditInfoForm(request.POST)
        if form.is_valid():
            #if form.gender == "F":
                #return HttpResponse("klsdaflj")
            basicInfo.gender=request.POST['gender']
            basicInfo.graduate_school =request.POST['graduate_school']
            basicInfo.signature = request.POST['signature']
            basicInfo.location = request.POST['location']
            basicInfo.save()
            contactInfo.qq=request.POST['qq']
            contactInfo.msn=request.POST['msn']
            contactInfo.save()
            return HttpResponseRedirect('../myinfo/')
        else:
            c = Context({"username":username,
                        "achievement":achievement,
                        "signature":signature,
                        "last_login":last_login,
                        'logined':logined,
                        "form":form})
            return render_to_response('editmyinfo.htm', c) 
    else:
        form =EditInfoForm({"gender":gender,
                                    "graduate_school":graduate_school,
                                    "location":location,
                                    "qq":qq,
                                    'msn':msn,
                                    'signature':signature})
       
        c = Context({"username":username,
                    "achievement":achievement,
                    "signature":signature,
                    "last_login":last_login,
                    'logined':logined,
                    "form":form})
        return render_to_response('editmyinfo.htm', c)
    
def changepassword(request):
    try:
        id =request.session['member_id']
    except KeyError:
        return HttpResponse('You have not login,and have no right of accessing!')
    logined =True
    
    user = User.objects.get(id = id)
    username = user.username
    last_login = user.last_login
    basicInfo = user.userbasicinfo
    achievement = basicInfo.achievement
    signature = basicInfo.signature

    if request.POST:
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            user.set_password(request.POST['password2'])
            user.save()
            form =ChangePasswordForm()
            c = Context({"username":username,
                        "achievement":achievement,
                        "signature":signature,
                        "last_login":last_login,
                        'logined':logined,
                        'form':form,
                        'setting':True})
            return render_to_response('changepassword.htm', c)
        else:
            c = Context({"username":username,
                        "achievement":achievement,
                        "signature":signature,
                        "last_login":last_login,
                        'logined':logined,
                        "form":form,
                        'setting':False})
            return render_to_response('changepassword.htm', c) 
    else:
        form =ChangePasswordForm()
        c = Context({"username":username,
                    "achievement":achievement,
                    "signature":signature,
                    "last_login":last_login,
                    'logined':logined,
                    'form':form,
                    'setting':False})
       
        return render_to_response('changepassword.htm', c)   

def friends(request):
    try:
        id =request.session['member_id']
    except KeyError:
        return HttpResponse('You have not login,and have no right of accessing!')
    logined =True
    
    user = User.objects.get(id = id)
    username = user.username
    last_login = user.last_login
    basicInfo = user.userbasicinfo
    achievement = basicInfo.achievement
    signature = basicInfo.signature
    c = Context({"username":username,
                "achievement":achievement,
                "signature":signature,
                "last_login":last_login,'logined':logined})
    return render_to_response('home.htm', c)

def logout(request):
    try:
        del request.session['member_id']
    except KeyError:
        pass
    form = LoginForm()
    return HttpResponseRedirect('../')

    


    
    
    






