from gansha.userAdmin.models import UserForm
from gansha.settings import MEDIA_ROOT,MEDIA_URL
from gansha.event.models import Event

from django.http import HttpResponse
from django.http import HttpResponseRedirect
import datetime, random, sha
from django.shortcuts import render_to_response, get_object_or_404
from django.core.mail import send_mail
from gansha.userAdmin.models import UserProfile,UserBasicInfo,ContactInfo,Friends,FriendRequest
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
                      'gansha@foxmail.com',
                      [new_user.email])
            email_url = new_user.email.split('@')[-1]
            return render_to_response('register.htm', {'created': True,
                                                       'email':new_user.email,
                                                       'email_url':email_url})
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

def index(request):
    #user has been logined,
    #improve1:session doesn't work...
    #improve2:after flush,the error info maitain!
    if request.session.get('member_id',0):
          return HttpResponseRedirect('home/')
    
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
        logined =True
    except KeyError:
        return HttpResponse('You have not login,and have no right of accessing!')
    
    user = User.objects.get(id = id)
    basicInfo = user.userbasicinfo
    request.session['username'] = user.username
    request.session['headshot'] = MEDIA_URL + str(basicInfo.headshot)
    request.session['achievement'] = basicInfo.achievement
    request.session['signature'] = basicInfo.signature
    request.session['last_login'] = user.last_login
    
    request_friend = FriendRequest.objects.filter(other_user = user)
    friends = Friends.objects.filter(username=user)

    event_list = Event.objects.filter( user_id=user )
    c = Context({"username":request.session['username'],
                 "headshot":request.session['headshot'],
                 "achievement":request.session['achievement'],
                 "signature":request.session['signature'],
                 "last_login":request.session['last_login'],
                 'logined':logined,
                 'request_friend':request_friend,
                 'friends':friends,
                 'event_list':event_list,
                 })
    return render_to_response('home.htm', c)

def myinfo(request):
    try:
        id =request.session['member_id']
    except KeyError:
        return HttpResponse('You have not login,and have no right of accessing!')
    logined =True
    
    user = User.objects.get(id = id)
 
    basicInfo = user.userbasicinfo
    achievement = basicInfo.achievement
    signature = basicInfo.signature
    gender = basicInfo.gender
    graduate_school = basicInfo.graduate_school
    location = basicInfo.location

    contactInfo = user.contactinfo
    qq = contactInfo.qq
    msn = contactInfo.msn
    
    c = Context({"username":request.session['username'],
                 "headshot":request.session['headshot'],
                 "achievement":request.session['achievement'],
                 "signature":request.session['signature'],
                 "last_login":request.session['last_login'],
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
        form = EditInfoForm(request.POST,request.FILES)
        if form.is_valid():
            #get headshot image,and store it
            f = request.FILES['headshot']
            if f:
                fext=f.name.split('.')[-1]
                fname=str(user.id)+'.'+fext
                basicInfo.headshot=fname          
                request.session['headshot'] = MEDIA_URL+str(basicInfo.headshot)
                destination = open(MEDIA_ROOT+fname,'wb+')
                for chunk in f.chunks():
                    destination.write(chunk)
            basicInfo.gender = form.cleaned_data['gender']
            basicInfo.graduate_school = form.cleaned_data['graduate_school']
            basicInfo.signature = form.cleaned_data['signature']
            basicInfo.location = form.cleaned_data['location']
            basicInfo.save()
            contactInfo.qq=form.cleaned_data['qq']
            contactInfo.msn=form.cleaned_data['msn']
            contactInfo.save()
            
            request.session['achievement'] = basicInfo.achievement
            request.session['signature'] = basicInfo.signature
            return HttpResponseRedirect('../myinfo/')
        else:
            c = Context({"username":request.session['username'],
                         "headshot":request.session['headshot'],
                         "achievement":request.session['achievement'],
                         "signature":request.session['signature'],
                         "last_login":request.session['last_login'],
                         "logined":logined,
                         "form":form})
            return render_to_response('editmyinfo.htm', c) 
    else:
        form =EditInfoForm({"gender":gender,
                            "graduate_school":graduate_school,
                            "location":location,
                            "qq":qq,
                            'msn':msn,
                            'signature':signature})
       
        c = Context({"username":request.session['username'],
                     "headshot":request.session['headshot'],
                     "achievement":request.session['achievement'],
                     "signature":request.session['signature'],
                     "last_login":request.session['last_login'],
                     "logined":logined,
                     "form":form})
        return render_to_response('editmyinfo.htm', c)
    
def changepassword(request):
    try:
        id =request.session['member_id']
    except KeyError:
        return HttpResponse('You have not login,and have no right of accessing!')
    logined =True
    
    user = User.objects.get(id = id)
 
    if request.POST:
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            user.set_password(request.POST['password2'])
            user.save()
            form =ChangePasswordForm()
            c = Context({"username":request.session['username'],
                         'headshot':request.session['headshot'],
                         "achievement":request.session['achievement'],
                         "signature":request.session['signature'],
                         "last_login":request.session['last_login'],
                         'logined':logined,
                         'form':form,
                         'setting':True})
            return render_to_response('changepassword.htm', c)
        else:
            c = Context({"username":request.session['username'],
                         'headshot':request.session['headshot'],
                         "achievement":request.session['achievement'],
                         "signature":request.session['signature'],
                         "last_login":request.session['last_login'],
                         'logined':logined,
                         "form":form,
                         'setting':False})
            return render_to_response('changepassword.htm', c) 
    else:
        form =ChangePasswordForm()
        c = Context({"username":request.session['username'],
                     'headshot':request.session['headshot'],
                     "achievement":request.session['achievement'],
                     "signature":request.session['signature'],
                     "last_login":request.session['last_login'],
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
    friends = Friends.objects.filter(username=user)
  
    c = Context({"username":request.session['username'],
                 'headshot':request.session['headshot'],
                 "achievement":request.session['achievement'],
                 "signature":request.session['signature'],
                 "last_login":request.session['last_login'],
                 'logined':logined,
                 'friends':friends})
    return render_to_response('friend.htm', c)

def removefriend(request):
    try:
        id =request.session['member_id']
    except KeyError:
        return HttpResponse('You have not login,and have no right of accessing!')
    logined =True
    
    user = User.objects.get(id = id)
    uid = request.POST['uid']
    otheruser =User.objects.get(id = uid)
 
    try:
        friend = Friends.objects.get(username=user,friend_name=otheruser)
        friend.delete()
        friend = Friends.objects.get(username=otheruser,friend_name=user)
        friend.delete()
    except:
        pass
    return HttpResponseRedirect('../friends')

def search(request):
    try:
        id =request.session['member_id']
    except KeyError:
        return HttpResponse('You have not login,and have no right of accessing!')
    logined =True
      
    search_value=request.GET['search_value']
    search_value=search_value.lstrip()
    search_value=search_value.rstrip()
    ret=[]
    if("1" == request.GET['search_kind']):           
        ret=User.objects.filter(username__contains=search_value)
        
    c = Context({"username":request.session['username'],
                 'headshot':request.session['headshot'],
                 "achievement":request.session['achievement'],
                 "signature":request.session['signature'],
                 "last_login":request.session['last_login'],
                 'ret':ret,
                 'search_value':search_value,
                 'logined':logined})
    return render_to_response('findfriend.htm', c)

def acceptfriend(request):
    try:
        id =request.session['member_id']
    except KeyError:
        return HttpResponse('You have not login,and have no right of accessing!')
    logined =True
    
    user = User.objects.get(id = id)
    uid = request.POST['uid']
    otheruser =User.objects.get(id = uid)
    try:
        friend = Friends.objects.get(username=user,friend_name=otheruser)
    except:
        friend_add = Friends(username=user,friend_name=otheruser)
        friend_add.save()
        friend_add = Friends(username=otheruser,friend_name=user)
        friend_add.save()

    try:
        requestfriend = FriendRequest.objects.get(request_user=otheruser,other_user=user)
        requestfriend.delete()
    except:
        pass
    
    return HttpResponseRedirect('../home')

def deny(request):
    try:
        id =request.session['member_id']
    except KeyError:
        return HttpResponse('You have not login,and have no right of accessing!')
    logined =True
    
    user = User.objects.get(id = id)
    uid = request.POST['uid']
    otheruser =User.objects.get(id = uid)

    try:
        requestfriend = FriendRequest.objects.get(request_user=otheruser,other_user=user)
        requestfriend.delete()
    except:
        pass
    
    return HttpResponseRedirect('../home')

def addfriend(request):
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

    msg=""
    search_value=""
    if request.POST:
        msg=request.POST['msg']
        search_value=request.POST['search_value']
        uid = request.POST['uid']
        otheruser = User.objects.get(id = uid)
        msg=msg.lstrip()
        msg=msg.rstrip()
        try:
            friend_add = FriendRequest.objects.get(request_user=user,other_user=otheruser)
            friend_add.message=msg
        except:
            friend_add = FriendRequest(request_user=user,other_user=otheruser,message=msg)
         
        friend_add.save()
        
    return HttpResponseRedirect('../search/?search_value=%s&search_kind=1'%search_value)

def logout(request):
    try:
        del request.session['member_id']
    except KeyError:
        pass
    form = LoginForm()
    return HttpResponseRedirect('../')

    


    
    
    






