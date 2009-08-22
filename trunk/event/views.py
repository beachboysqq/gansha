from google.appengine.api import users,memcache
from google.appengine.ext import db
from google.appengine.ext.db import Key
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.template import Context
from django.contrib.auth.decorators import login_required
from userAdmin.models import User_profile
from event.models import Event,Subevent,History,Concern
from blog.models import Blog
import datetime

@login_required
def add_event(request):
    user = users.get_current_user()
    if not user:
        return render_to_response('error.htm',{'error':'You have not login,and have no right of accessing!'})
    
    if request.method == 'POST':
        #try:
        if request.POST['is_public'] =='1':
            is_public = True
        else:
            is_public = False
        event = Event(title=request.POST['title'],
                      desc=request.POST['desc'],
                      is_public=is_public)
        event.user = user
        event.put()
        return HttpResponseRedirect( '../event/?event=%s' % str(event.key()) )
        #except:
        #    return...error
    else:
        c = Context({"uname":memcache.get('uname'),
                     "headshot":memcache.get('headshot'),
                     "rank":memcache.get('rank'),
                     "sign":memcache.get('sign'),
                     'logouturl':memcache.get('logouturl'),
                     "last_login":memcache.get('last_login'),
                     'is_admin':True,
                     'event':Event(),
                     })
        return render_to_response( 'newevent.htm',c )
        
@login_required
def edit_event(request):
    user = users.get_current_user()
    if not user:
        return render_to_response('error.htm',{'error':'You have not login,and have no right of accessing!'})
    ekey = Key(memcache.get('event'))
    event = Event.get(ekey)
    
    if request.method == 'POST':
        #try:
        if request.POST['is_public'] =='1':
            event.is_public = True
        else:
            event.is_public = False
        event.title=request.POST['title']
        event.desc=request.POST['desc']
        event.put()
        return HttpResponseRedirect( '../event/?event=%s' % str(event.key()) )
        #except:
        #    return...error
    else:
        c = Context({"uname":memcache.get('uname'),
                     "headshot":memcache.get('headshot'),
                     "rank":memcache.get('rank'),
                     "sign":memcache.get('sign'),
                     'logouturl':memcache.get('logouturl'),
                     "last_login":memcache.get('last_login'),
                     'is_admin':True,
                     'event':event,
                     })
        return render_to_response( 'newevent.htm',c )
    
@login_required
def del_event(request):
    user = users.get_current_user()
    if not user:
        return render_to_response('error.htm',{'error':'You have not login,and have no right of accessing!'})
    m_user = User_profile.gql('where user = :1',user).get()
    m_user.rank -=0
    if m_user.rank < 0:
        m_user.rank = 0
    ekey = Key(memcache.get('event'))
    memcache.delete('event')
    event = Event.get(ekey)
    # delete sub events
    se_list = Subevent.gql("where event = :1",event)
    db.delete( se_list )
    
    event.delete()
    return HttpResponse("deleted")

def event(request):
    user = users.get_current_user()
    if not user:
        return render_to_response('error.htm',{'error':'You have not login,and have no right of accessing!'})
    try:
        ekey = request.GET['event']
        # record the current event for further useage
        memcache.set('event',ekey)
    except KeyError:
        ekey = memcache.get('event')
        if not ekey:
            raise Http404
    
    event = Event.get(Key(ekey))
    # vistor is a guest,get the host
    if user != event.user:
        is_admin = False
    else:
        # visitor is host:the owner of this page
        is_admin = True
    
    # update host user's info in memcache 
    if event.user != users.User(memcache.get('host_email')):
        m_user = User_profile.gql('where user = :1',event.user).get()
        memcache.set('host_email',event.user.email())
        memcache.set('uname',event.user.nickname())
        memcache.set('rank',m_user.rank)
        memcache.set('sign',m_user.sign)
        memcache.set('last_login',m_user.last_login)
        memcache.set('headshot',m_user.headshot)

    # get sub event of this event
    se_list = Subevent.gql("where event = :1 order by start_date,end_date",event) 
    # check up wheather sub event is expired
    for se in se_list:
        if se.isexpired==False and se.end_date < datetime.date.today():
            se.isexpired = True
            se.put()
    # get host's history operation on this event
    history_li = History.all().filter('event =',event).order('-date')
    # get blogs about this event
    blog_li = Blog.all().filter('event =',event )
    # get concern update information on this event
    
    # get users who concern me on this event

    c = Context({"uname":memcache.get('uname'),
                 "headshot":memcache.get('headshot'),
                 "rank":memcache.get('rank'),
                 "sign":memcache.get('sign'),
                 'logouturl':memcache.get('logouturl'),
                 "last_login":memcache.get('last_login'),
                 'is_admin':is_admin,
                 'event':event,
                 'se_list':se_list,
                 'num_se':se_list.count(20),
                 'history_li':history_li,
                 'num_history_records':history_li.count(10),
                 'blog_li':blog_li,
                 'num_blogs':blog_li.count(100),
                 })
    return render_to_response('event.htm',c)

@login_required
def add_sub_event(request):
    user = users.get_current_user()
    if not user:
        return HttpResponse('error')

    pekey = Key(memcache.get('event'))
    if not pekey:
        return render_to_response('error.htm',{'error':'No memcache find,please login again!'})
    pe = Event.get(pekey)
    
    if request.method == 'POST':
        se = Subevent(user=user,event=pe,content=request.POST['content'])
        # treat date from str to datetime type
        start_date = request.POST['start_date']
        li = start_date.split('-')
        se.start_date = datetime.date( int(li[0]),int(li[1]),int(li[2]))
        
        end_date = request.POST['end_date']
        li = end_date.split('-')
        se.end_date = datetime.date( int(li[0]),int(li[1]),int(li[2]))
        # adjust the parent event's start_date and end_date
        if se.start_date < pe.start_date:
            pe.start_date = se.start_date
        if se.end_date > pe.end_date:
            pe.end_date = se.end_date
        # adjust progress of parent event,mutipled by 100
        pe.num_se +=1
        pe.progress = pe.progress*(pe.num_se-1)/pe.num_se
        pe.put()
        
        if se.end_date < datetime.date.today():
            se.isexpired = True
        else:
            se.isexpired = False
        se.put()
        return HttpResponse( se.key() )
    else:
        return HttpResponse("error")

@login_required
def edit_sub_event( request ):
    user = users.get_current_user()
    if not user:
        return HttpResponse('error')

    try:
        sekey = Key(request.POST['key'])
        se = Subevent.get(sekey)
        se.content = request.POST['content']
        pekey = Key(memcache.get('event'))
        pe = Event.get(pekey)
        # treat date from str to datetime type
        start_date = request.POST['start_date']
        li = start_date.split('-')
        se.start_date = datetime.date( int(li[0]),int(li[1]),int(li[2]))
       
        end_date = request.POST['end_date']
        li = end_date.split('-')
        se.end_date = datetime.date( int(li[0]),int(li[1]),int(li[2]))
        # adjust the parent event's start_date and end_date
        if se.start_date < pe.start_date:
            pe.start_date = se.start_date
        if se.end_date > pe.end_date:
            pe.end_date = se.end_date
        pe.put()
    except:
        return HttpResponse('error')
    
    if se.end_date < datetime.date.today():
        se.isexpired = True
    else:
        se.isexpired = False
    se.put()
    return HttpResponse( se.isexpired )

@login_required
def del_sub_event(request):
    user = users.get_current_user()
    if not user:
        return HttpResponse('error')
    try:
        sekey = Key(request.POST['key'])
        pekey = Key(memcache.get('event'))
    except:
        return HttpResponse('error')
    
    se = Subevent.get(sekey)
    pe = Event.get(pekey)
    pe.num_se -=1
    if pe.num_se!=0:
        pe.progress = pe.progress*(pe.num_se+1)/pe.num_se
    else:
        pe.progress = 0
        
    if pe.start_date == se.start_date:
        pe.start_date = Subevent.all().order('start_date').get().start_date
    if pe.end_date == se.end_date:
        pe.end_date = Subevent.all().order('-end_date').get().end_date
    pe.put()
    se.delete()
    return HttpResponse( str(sekey) )

@login_required
def done_sub_event(request):
    user = users.get_current_user()
    if not user:
        return HttpResponse('error')
    
    try:
        sekey = Key(request.POST['key'])
        pekey = Key(memcache.get('event'))
        is_done = request.POST['is_done']
    except:
        return HttpResponse('error')
    # update event,sub_event,history info
    se = Subevent.get(sekey)
    pe = Event.get(pekey)
    if is_done == 'true':
        se.is_done = True
        se.end_date = datetime.date.today()
        hi = History()
        hi.event = pe
        hi.content = "acomplished:"+se.content
        hi.user = user
        hi.put()
        #adjust parent event's progress
        pe.progress = pe.progress+100/pe.num_se
        if pe.progress == 100:
            pe.is_done = True
    else:
        se.is_done = False
        if pe.progress == 100:
            pe.is_done = False
        pe.progress = pe.progress-100/pe.num_se
    pe.put()
    se.put()   
    return HttpResponse( se.key() )

def events_doing(request):
    user = users.get_current_user()
    if not user:
        return render_to_response('error.htm',{'error':'You have not login,and have no right of accessing!'})

    # vistor is a guest,get the host
    host = users.User(memcache.get('host_email'))
    # m_user = User_profile.gql('where user = :1',host).get()

    if user.email() != host.email():
        is_admin = False
    else:
        is_admin = True
    events = Event.all().filter('user =',host ).filter( 
        'start_date <=',datetime.date.today() ).filter('is_done =',False ).order('start_date')
        
    c = Context({"uname":memcache.get('uname'),
                 "headshot":memcache.get('headshot'),
                 "rank":memcache.get('rank'),
                 "sign":memcache.get('sign'),
                 'logouturl':memcache.get('logouturl'),
                 "last_login":memcache.get('last_login'),
                 'events':events,
                 'kind':'doing',
                 'is_admin':is_admin,
                 })
    return render_to_response( 'event_list.htm',c)

def events_todo(request):
    user = users.get_current_user()
    if not user:
        return render_to_response('error.htm',{'error':'You have not login,and have no right of accessing!'})

    # vistor is a guest,get the host
    host = users.User(memcache.get('host_email'))
    
    if user != host:
        is_admin = False
    else:
        is_admin = True
    events = Event.all().filter('user =',host ).filter( 
        'start_date >',datetime.date.today() ).filter('is_done =',False ).order('start_date')
        
    c = Context({"uname":memcache.get('uname'),
                 "headshot":memcache.get('headshot'),
                 "rank":memcache.get('rank'),
                 "sign":memcache.get('sign'),
                 'logouturl':memcache.get('logouturl'),
                 "last_login":memcache.get('last_login'),
                 'events':events,
                 'kind':'todo',
                 'is_admin':is_admin,
                 })
    return render_to_response( 'event_list.htm',c)
def events_done(request):
    user = users.get_current_user()
    if not user:
        return render_to_response('error.htm',{'error':'You have not login,and have no right of accessing!'})

    # vistor is a guest,get the host
    host = users.User(memcache.get('host_email'))
    if user != host:
        is_admin = False
    else:
        is_admin = True
    events = Event.all().filter('user =',host ).filter('progress =',100 ).order('start_date')
        
    c = Context({"uname":memcache.get('uname'),
                 "headshot":memcache.get('headshot'),
                 "rank":memcache.get('rank'),
                 "sign":memcache.get('sign'),
                 'logouturl':memcache.get('logouturl'),
                 "last_login":memcache.get('last_login'),
                 'events':events,
                 'kind':'done',
                 'is_admin':is_admin,
                 })
    return render_to_response( 'event_list.htm',c)

@login_required
def add_to_concern( request ):
    event = Event.get( request.POST['eid'] )
    c_event = Event.get( request.POST['ce_id'] )
    
    try:
       concern = Concern.all().filter( 'user =',event.user,'event =',event,'c_event=',c_event)
    except:
        concern = Concern( use=event.user,event=event,c_event=c_event)
        concern.put()
    return HttpResponse("added")

@login_required
def remove_concern( request ):
    event = Event.get( request.POST['eid'] )
    c_event = Event.get( request.POST['ce_id'] )
    
    concern = Concern.all().filter( 'user =',event.user,'event=',event,'c_event=',ce_event)
    concern.delete()
    return HttpResponse("removed")

