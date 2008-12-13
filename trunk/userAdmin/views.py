from gansha.userAdmin.models import UserProfile,UserBasicInfo,ContactInfo,Friends,FriendRequest
from gansha.userAdmin.forms import RegistrationForm,LoginForm,EditInfoForm,ChangePasswordForm
from gansha.userAdmin.models import UserForm
from gansha.settings import MEDIA_ROOT,MEDIA_URL
from gansha.event.models import Event,Sub_event,History
from gansha.blog.models import Blog
import datetime
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.db.models import Q
import datetime, random, sha
from django.shortcuts import render_to_response, get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.template import Context, Template
from django.http import Http404

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
    #user come back home,wellcome:)
    if request.session.get('member_id',0):
        request.session['who'] = request.session['member_id']
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
                #initialize session
                request.session['member_id'] = m.id
                request.session['who'] = m.id
                if not request.POST.has_key('auto_remember'):
                    request.session.set_expiry(0)
                
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
    ##judge wheather the current visitor is the page owner or other people
    if request.GET.has_key('user') and request.GET['user']!=id:
        is_admin = False
        request.session['who'] = request.GET['user']
        uid = request.session['who']
    elif request.session['who']!=id:
        is_admin = False
        uid = request.session['who']
    else:
        is_admin = True
        uid = id
        
    user = User.objects.get(id = uid)
    basicInfo = user.userbasicinfo
    request.session['username'] = user.username
    request.session['headshot'] = MEDIA_URL + str(basicInfo.headshot)
    request.session['achievement'] = basicInfo.achievement
    request.session['signature'] = basicInfo.signature
    request.session['last_login'] = user.last_login
    
    request_friend = FriendRequest.objects.filter( receiver=user )
    friends = Friends.objects.filter( user_id=user )

    event_list = Event.objects.filter( user_id=user )
    se_list = Sub_event.objects.filter( event_id__in=event_list ).filter(
        isdone=False ).filter( start_date__lte=datetime.date.today() )
    hi_list = History.objects.filter( event_id__in=event_list )
    
    c = Context({"username":request.session['username'],
                 "headshot":request.session['headshot'],
                 "achievement":request.session['achievement'],
                 "signature":request.session['signature'],
                 "last_login":request.session['last_login'],
                 'logined':logined,
                 'request_friend':request_friend,
                 'friends':friends,
                 'se_list':se_list,
                 'hi_list':hi_list,
                 'is_admin':is_admin,
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
    logined = True
    
    uid = request.session['who']
    is_admin = (uid==id)
    user = User.objects.get(id = uid)
    friends = Friends.objects.filter( user_id=user )
  
    li = []
    for friend in friends:
        sub_li = [friend]
        count = History.objects.filter( user_id=friend.myfriend ).count()
        if count>3:
            count = 3
        sub_li.append( History.objects.filter( user_id=friend.myfriend ).order_by('date')[0:count] )
        li.append( sub_li )
    
    c = Context({"username":request.session['username'],
                 'headshot':request.session['headshot'],
                 "achievement":request.session['achievement'],
                 "signature":request.session['signature'],
                 "last_login":request.session['last_login'],
                 'logined':logined,
                 'friends':li,
                 'is_admin':is_admin,
                 })
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
        friend = Friends.objects.get( user_id=user,myfriend=otheruser )
        friend.delete()
        #friend = Friends.objects.get( user_id=otheruser,myfriend=user)
        #friend.delete()
    except:
        pass
    return HttpResponse('removed')

def search(request):
    try:
        id =request.session['member_id']
    except KeyError:
        return HttpResponse('You have not login,and have no right of accessing!')
    logined =True
      
    ##if on other's page,go back home
    user = User.objects.get( id=id )
    if request.session['who'] != id:
        request.session['who'] = id
        ##reset user information for session
        basicInfo = user.userbasicinfo
        request.session['username'] = user.username
        request.session['headshot'] = MEDIA_URL + str(basicInfo.headshot)
        request.session['achievement'] = basicInfo.achievement
        request.session['signature'] = basicInfo.signature
        request.session['last_login'] = user.last_login 
        
    search_value=request.GET['search_value']
    search_value=search_value.lstrip()
    search_value=search_value.rstrip()
    search_kind = request.GET['search_kind']
    
    dict = {"username":request.session['username'],
    'headshot':request.session['headshot'],
    "achievement":request.session['achievement'],
    "signature":request.session['signature'],
    "last_login":request.session['last_login'],
    'search_value':search_value,
    'logined':logined}
    ret=[]
    if("username" == search_kind ):
        ret = User.objects.filter( username__contains=search_value ).exclude(id=1)
        dict['ret'] = ret
        dict['counter'] = len( ret )
        return render_to_response('findfriend.htm',Context(dict) )
    elif("event" == search_kind ):
        ret = Event.objects.filter( Q(title__contains=search_value)|
                                    Q(description__contains=search_value)|
                                    Q(isprivacy=False)
                                   ).distinct()
        myevents = Event.objects.filter( user_id=user )
        dict['myevents'] = myevents
        dict['ret'] = ret
        dict['counter'] = len( ret )
        return render_to_response( 'findevent.htm',Context(dict) )
    else:
        ret = Blog.objects.filter( Q(title__contains=search_value)|
                                    Q(content__contains=search_value)
                                   ).distinct()
        dict['ret'] = ret
        dict['counter'] = len( ret )
        return render_to_response('findblog.htm',Context(dict) )

##accept someone's request and become friends with he/she
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
        friend = Friends.objects.get( user_id=user,myfriend=otheruser )
    except:
        friend_add = Friends( user_id=user,myfriend=otheruser )
        friend_add.save()
        friend_add = Friends( user_id=otheruser,myfriend=user )
        friend_add.save()

    try:
        requestfriend = FriendRequest.objects.get( sender=otheruser,receiver=user )
        requestfriend.delete()
    except:
        pass
    return HttpResponse('done')

def deny(request):
    try:
        id =request.session['member_id']
    except KeyError:
        return HttpResponse('You have not login,and have no right of accessing!')
    logined =True
    
    user = User.objects.get(id = id)
    uid = request.POST['uid']
    otheruser =User.objects.get( id=uid )

    try:
        requestfriend = FriendRequest.objects.get( sender=otheruser,receiver=user)
        requestfriend.delete()
    except:
        pass
    return HttpResponse('done')

##after send friends request,record the request
def addfriend(request):
    try:
        id =request.session['member_id']
        user = User.objects.get(id = id)
    except KeyError:
        return HttpResponse('You have not login,and have no right of accessing!')
   
    if request.method == 'POST':
        msg = request.POST['message'].strip()
        uid = request.POST['uid']
        receiver = User.objects.get( id=uid )
        
        friend_add = FriendRequest( sender=user,receiver=receiver,message=msg )
        friend_add.save()
        return HttpResponse('sended')
    else:
        raise Http404

def logout(request):
    try:
        del request.session['member_id']
    except KeyError:
        pass
    form = LoginForm()
    return HttpResponseRedirect('../')

    


    
    
    






