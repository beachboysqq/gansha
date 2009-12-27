#coding=utf-8
from google.appengine.api import users,memcache
from google.appengine.ext.db import Key
from google.appengine.ext import db
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.template import Context
from django.contrib.auth.decorators import login_required
from userAdmin.models import User_profile,Friends,FriendRequest
from event.models import Event,Subevent,History
from blog.models import Blog,Comment,Mes
from util.util import reset_memcache,now,today
import datetime

def index(request):
    user = users.get_current_user()
    if not user:
        loginurl = users.create_login_url('/myhome')
        return render_to_response('index.htm',{'loginurl':loginurl})
    else:
        return HttpResponseRedirect('/myhome')

#deploy home content
def home_context( host ):
    user = users.get_current_user()
    host = User_profile.gql('where uid = :1',memcache.get('hostid')).get().user
    # get ongoing sub events
    se_list = Subevent.all().filter('user =',host).filter( 'is_done =',False ).filter( 'start_date <=',today() )
    # get recent history operation
    hi_list = History.all().filter( 'user =',host ).order('-publish_time').fetch(5)
    # get my friends
    friends = Friends.all().filter( 'user =',host )
    # get friend requests
    request_friend = FriendRequest.all().filter('receiver =',host)
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
                 'is_admin':memcache.get('hostid')==user.user_id(),
                 'request_friend':request_friend,
                 'friends':friends, 
                 'se_list':se_list,
                 'hi_list':hi_list,
                 'comments':comments,
                 'mes_li':mes_li,
                 })
    return c

@login_required
#my home,login or come back
def myhome(request):
    user = users.get_current_user()
    hostid = user.user_id()
    me = User_profile.gql('where uid = :1',hostid).get()
    if not me:
        me = User_profile(user=user,uid=user.user_id())
        me.put()           

    if not memcache.get('hostid'): # if not find,will return None
        memcache.set('last_login',me.last_login)
        memcache.set('logouturl', users.create_logout_url('/'))
        
    # record basic info for user into session
    reset_memcache( me )

    # update last_login info 
    me.last_login = today()
    me.put()
    c = home_context( me )
    return render_to_response('home.htm',c)

#visit others home
@login_required
def home(request):
    #come in by ohter links
    if request.GET.has_key('user'):
        hostid = request.GET['user']
        m_user = User_profile.gql('where uid = :1',hostid).get()
        reset_memcache( m_user )
    else:
        #not jump in
        hostid = memcache.get('hostid')
        m_user = User_profile.gql('where uid = :1',hostid).get()
    c = home_context( m_user )
    return render_to_response('home.htm',c)

@login_required
def myinfo(request):
    user = users.get_current_user()

    m_user = User_profile.gql('where uid = :1',memcache.get('hostid') ).get()
    return render_to_response('myinfo.htm',{'user':m_user,
                                            'uname':m_user.user.nickname(),
                                            "headshot":memcache.get('headshot'),
                                            "sign":memcache.get('sign'),
                                            "rank":memcache.get('rank'),
                                            'logouturl':memcache.get('logouturl'),
                                            "last_login":memcache.get('last_login'),                               
                                            'is_admin':memcache.get('hostid')==user.user_id(),
                                            })

@login_required
def editmyinfo(request):
    user = users.get_current_user()
    m_user = User_profile.gql('where user = :1',user).get()
        
    # collect  data submitted from form and update m_user
    if request.POST:
        m_user.headshot = request.POST['headshot'].strip()
        m_user.sign = request.POST['sign'].strip()
        m_user.uname = request.POST['uname'].strip()
        m_user.gender = request.POST['gender'].strip()
        try:
            m_user.age = int(request.POST['age'].strip())
        except:
            pass
        m_user.addr = request.POST['addr'].strip()
        m_user.blog = request.POST['blog'].strip()
        m_user.other = request.POST['other'].strip()
        m_user.is_public = request.POST['is_public'] =='1'
        m_user.put()
        # reset memcache
        memcache.set('headshot',m_user.headshot)
        memcache.set('sign',m_user.sign)
        return HttpResponseRedirect('../myinfo/')
    else:
        return render_to_response('editmyinfo.htm',{'uname':m_user.user.nickname(),
                                                    "headshot":memcache.get('headshot'),
                                                    "sign":memcache.get('sign'),
                                                    'gender':m_user.gender,
                                                    'age':m_user.uname,
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

#deal with search request
@login_required
def search(request):
    user = users.get_current_user()
    # m_user = User_profile.gql('where uid = :1',user.user_id()).get()
    # if not m_user:
    #     m_user = User_profile(user=user)
    ##if on other's page,go back home
    # if memcache.get('hostid')!=user.user_id():
    #     memcache.set('hostid',user.user_id())
    #     memcache.set('uname',user.nickname())
    #     memcache.set('rank',m_user.rank)
    #     memcache.set('sign',m_user.sign)
    #     memcache.set('headshot',m_user.headshot)
    #     memcache.set('last_login',m_user.last_login)
        
    search_value=request.GET['search_value'].strip()
    search_kind = request.GET['search_kind']
    
    dict = {"uname":memcache.get('uname'),
            'headshot':memcache.get('headshot'),
            "rank":memcache.get('rank'),
            "sign":memcache.get('sign'),
            "last_login":memcache.get('last_login'),
            'logouturl':memcache.get('logouturl'),
            'search_value':search_value,
            'is_admin':memcache.get('hostid')==user.user_id(),
            'myid':user.user_id()}
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

@login_required
def friends(request):
    user = users.get_current_user()
    
    host = users.User(memcache.get('hostid'))
    if host == user:
        is_admin = True
    else:
        is_admin = False
    friends = Friends.all().filter('user =',host )
    li = []
    for friend in friends:
        sub_li = [friend]
        sub_li.append( History.all().filter( 'user =',friend.myfriend ).order('-publish_time').fetch(3) )
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

@login_required
def addfriend(request):
    user = users.get_current_user()
    
    if request.method == 'POST':
        he = User_profile.gql('where uid = :1',request.POST['uemail']).get().user
        msg = request.POST['message'].strip()        
        friend_add = FriendRequest( sender=user,receiver=he,message=msg )
        friend_add.put()
        return HttpResponse('sended')
    else:
        raise Http404

@login_required
def acceptfriend(request):
    user = users.get_current_user()
    he = User_profile.gql('where uid = :1',request.POST['uemail']).get().user
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

@login_required
def deny(request):
    user = users.get_current_user()
    he = User_profile.gql('where uid = :1',request.POST['uemail']).get().user
    try:
        requestfriend = FriendRequest.all().filter('sender =',he).filter('receiver =',user)
        requestfriend.delete()
    except:
        return HttpResponse('done')
    return HttpResponse('done')

@login_required
def removefriend(request):
    user = users.get_current_user()
    he = User_profile.gql('where uid = :1',request.POST['uemail']).get().user
    
    try:
        friend = Friends.all().filter('user =',user).filter('myfriend =',he)
        friend.delete()
        #friend = Friends.objects.get( user_id=otheruser,myfriend=user)
        #friend.delete()
    except:
        pass
    return HttpResponse('removed')

