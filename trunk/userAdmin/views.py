# -*- coding: utf-8 -*-
from google.appengine.api import users,memcache
from google.appengine.ext.db import Key
from google.appengine.ext import db
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.template import Context
from userAdmin.models import User_profile,Friends,FriendRequest
from event.models import Event,Subevent,History
from blog.models import Blog,Comment,Mes
import datetime

def index(request):
    user = users.get_current_user()
    if not user:
        loginurl = users.create_login_url('/myhome')
        return render_to_response('index.htm',{'loginurl':loginurl})
    else:
        return HttpResponseRedirect('/myhome')

def home(request,whose):
    user = users.get_current_user()
    # user have not login
    if not user:
        return render_to_response('error.htm',{'error':'You have not login,and have no right of accessing!'})
    else:
        if whose=='myhome':
            is_admin = True
            host = user
        else:
        #a visitor is coming...
            if request.GET.has_key('user'):
                host = users.User( request.GET['user'] )
                memcache.set('host_email',host.email())
                if host!=user:
                    is_admin = False
                else:
                    # user go home by get methon!
                    is_admin = True
            else:
                if memcache.get('host_email')==user.email():
                    is_admin = True
                else:
                    is_admin = False
                host = users.User(memcache.get('host_email'))
                
        m_user = User_profile.gql('where user = :1',host).get()
        if not m_user:
            m_user = User_profile(user=user)
            m_user.put()
            
        # record basic info for user into session
        memcache.set('host_email',host.email())
        memcache.set('uname',host.nickname())
        memcache.set('headshot',m_user.headshot)
        memcache.set('rank',m_user.rank)
        memcache.set('sign',m_user.sign)
        memcache.set('last_login',m_user.last_login)
        memcache.set('logouturl', users.create_logout_url('/'))
        
        # update last_login info 
        m_user.last_login = datetime.date.today()
        m_user.put()
        # get ongoing sub events
        se_list = Subevent.all().filter('user =',host).filter( 'is_done =',False ).filter( 'start_date <',datetime.date.today() )
        # get recent history operation
        hi_list = History.all().filter( 'user =',host ).fetch(5)
        # get my friends
        friends = Friends.all().filter( 'user =',host )
        # get friend requests
        request_friend = FriendRequest.all().filter( 'receiver =',host )
        # get recent comments
        comments = Comment.all().filter('receiver =',host).order('-publish_time').fetch(5)
        # get recent messages
        mes_li = Mes.all().filter('receiver =',host).order('-publish_time').fetch(5)

        c = Context({"uname":memcache.get('uname'),
                     "headshot":memcache.get('headshot'),
                     "rank":memcache.get('rank'),
                     "sign":memcache.get('sign'),
                     'logouturl':memcache.get('logouturl'),
                     "last_login":memcache.get('last_login'),
                     'is_admin':is_admin,
                     'request_friend':request_friend,
                     'friends':friends, 
                     'se_list':se_list,
                     'hi_list':hi_list,
                     'comments':comments,
                     'mes_li':mes_li,
                 })
        return render_to_response('home.htm',c)
       
def myinfo(request):
    user = users.get_current_user()
    # user have not login
    if not user:
        return render_to_response('error.htm',{'error':'You have not login,and have no right of accessing!'})

    # verify visit is host or guset by compare user to memcache.get('host_email')
    email = memcache.get('host_email')
    host = users.User(email)
    if user == host:
        is_admin = True
    else:
        is_admin =False
    m_user = User_profile.gql('where user = :1',host).get()
    return render_to_response('myinfo.htm',{'user':m_user,
                                            'uname':user.nickname(),
                                            "headshot":memcache.get('headshot'),
                                            "sign":memcache.get('sign'),
                                            "rank":memcache.get('rank'),
                                            'logouturl':memcache.get('logouturl'),
                                            "last_login":memcache.get('last_login'),                               
                                            'is_admin':is_admin,
                                            })

def editmyinfo(request):
    user = users.get_current_user()
    # user have not login
    if not user:
           return render_to_response('error.htm',{'error':'You have not login,and have no right of accessing!'})
    else:
        m_user = User_profile.gql('where user = :1',user).get()
        if not m_user:
            m_user = User_profile(user=user)
            
        # collect  data submitted from form and update m_user
        if request.POST:
            m_user.headshot = request.POST['headshot']
            m_user.sign = request.POST['sign']
            m_user.gender = request.POST['gender']
            try:
                m_user.age = int(request.POST['age'])
            except:
                pass
            m_user.addr = request.POST['addr']
            m_user.blog = request.POST['blog']
            m_user.other = request.POST['other']
            if request.POST['is_public'] =='1':
                is_public = True
            else:
                is_public = False
            # also mybe:is_public = {'1':True,'0':False}[request.POST['is_public']]
            m_user.is_public = is_public
            m_user.put()
            # reset memcache
            memcache.set('headshot',m_user.headshot)
            memcache.set('sign',m_user.sign)
            return HttpResponseRedirect('../myinfo/')
        else:
            return render_to_response('editmyinfo.htm',{'uname':user.nickname(),
                                                        "headshot":memcache.get('headshot'),
                                                        "sign":memcache.get('sign'),
                                                        'gender':m_user.gender,
                                                        'age':m_user.age,
                                                        'addr':m_user.addr,
                                                        'job':m_user.job,
                                                        'blog':m_user.blog,
                                                        'other':m_user.other,
                                                        "rank":memcache.get('rank'),
                                                        'logouturl':memcache.get('logouturl'),
                                                        "last_login":memcache.get('last_login'),          
                                                        'is_public':m_user.is_public,
                                                        'is_admin':True,
                                                        })
        
def search(request):
    user = users.get_current_user()
    # user have not login
    if not user:
           return render_to_response('error.htm',{'error':'You have not login,and have no right of accessing!'})
    else:
        m_user = User_profile.gql('where user = :1',user).get()
        if not m_user:
            m_user = User_profile(user=user)
    ##if on other's page,go back home
    if memcache.get('host_email')!=user.email():
        memcache.set('host_email',user.email())
        memcache.set('uname',user.nickname())
        memcache.set('rank',m_user.rank)
        memcache.set('sign',m_user.sign)
        memcache.set('headshot',m_user.headshot)
        memcache.set('last_login',m_user.last_login)
        
    search_value=request.GET['search_value']
    search_value=search_value.lstrip()
    search_value=search_value.rstrip()
    search_kind = request.GET['search_kind']
    
    dict = {"uname":memcache.get('uname'),
            'headshot':memcache.get('headshot'),
            "rank":memcache.get('rank'),
            "sign":memcache.get('sign'),
            "last_login":memcache.get('last_login'),
            'logouturl':memcache.get('logouturl'),
            'search_value':search_value,
            'is_admin':True,}
    ret=[]
    if("username" == search_kind ):
        ret = User_profile.all()
        dict['ret'] = ret
        dict['counter'] = ret.count(100)
        return render_to_response('findfriend.htm',Context(dict) )
    elif("event" == search_kind ):
        ret = Event.search_index.search( search_value ).fetch(10)
        myevents = Event.all().filter( 'user =',user )
        dict['myevents'] = myevents
        dict['ret'] = ret
        return render_to_response( 'findevent.htm',Context(dict) )
    else:
        ret = Blog.search_index.search( search_value ).fetch( 10 )
        dict['ret'] = ret
        return render_to_response('findblog.htm',Context(dict) )

def friends(request):
    user = users.get_current_user()
    # user have not login
    if not user:
        return render_to_response('error.htm',{'error':'You have not login,and have no right of accessing!'})
    
    host = users.User(memcache.get('host_email'))
    if host == user:
        is_admin = True
    else:
        is_admin = False
    friends = Friends.all().filter('user =',host )
    li = []
    for friend in friends:
        sub_li = [friend]
        sub_li.append( History.all().filter( 'user =',friend.myfriend ).order('date').fetch(3) )
        li.append( sub_li )
    
    c = Context({"uname":memcache.get('uname'),
                 "headshot":memcache.get('headshot'),
                 "rank":memcache.get('rank'),
                 "sign":memcache.get('sign'),
                 'logouturl':memcache.get('logouturl'),
                 "last_login":memcache.get('last_login'),
                 'friends':li,
                 'is_admin':is_admin,
                 })
    return render_to_response('friend.htm', c)

def addfriend(request):
    user = users.get_current_user()
    # user have not login
    if not user:
        return render_to_response('error.htm',{'error':'You have not login,and have no right of accessing!'})
    
    if request.method == 'POST':
        he = users.User(request.POST['uemail'])
        msg = request.POST['message'].strip()        
        friend_add = FriendRequest( sender=user,receiver=he,message=msg )
        friend_add.put()
        return HttpResponse('sended')
    else:
        raise Http404

def acceptfriend(request):
    user = users.get_current_user()
    # user have not login
    if not user:
        return render_to_response('error.htm',{'error':'You have not login,and have no right of accessing!'})

    he = users.User(request.POST['uemail'])
    try:
       # friend = Friends.all().filter('user =',user).filter('myfriend =',he )
        friend_add = Friends(user=user,myfriend=he)
        friend_add.put()
        friend_add = Friends(user=he,myfriend=user)
        friend_add.put()
    except:
        pass
    try:
        requestfriend = FriendRequest.all().filter('sender =',he).filter('receiver =',user )
        db.delete(requestfriend)
    except:
        pass
    return HttpResponse('done')

def deny(request):
    user = users.get_current_user()
    # user have not login
    if not user:
        return render_to_response('error.htm',{'error':'You have not login,and have no right of accessing!'})
    
    he = users.User(request.POST['uemail'])
    try:
        requestfriend = FriendRequest.all().filter('sender =',he).filter('receiver =',user)
        requestfriend.delete()
    except:
        return HttpResponse('done')
    return HttpResponse('done')

def removefriend(request):
    user = users.get_current_user()
    # user have not login
    if not user:
        return render_to_response('error.htm',{'error':'You have not login,and have no right of accessing!'})
    
    he = users.User(request.POST['uemail'])
    
    try:
        friend = Friends.all().filter('user =',user).filter('myfriend =',he)
        friend.delete()
        #friend = Friends.objects.get( user_id=otheruser,myfriend=user)
        #friend.delete()
    except:
        pass
    return HttpResponse('removed')

