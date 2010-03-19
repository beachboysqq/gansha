#coding=utf-8
from google.appengine.api import users,memcache
from google.appengine.ext import db
from google.appengine.ext.db import Key
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.template import Context
from event.models import Event,Subevent,History
from blog.models import Blog,Comment,Mes
from tip.models import Tip
from util.util import now,today
from my_settings import *
import datetime

def add_event(request):
    if not users.is_current_user_admin():
        return HttpResponseRedirect('/')
        
    if request.method == 'POST':
        is_public = request.POST['is_public'] =='1'
        event = Event(
                      title=request.POST['title'],
                      desc=request.POST['desc'],
                      publish_date=today(),
                      is_public=is_public)
        event.put()
        return HttpResponseRedirect( '../event/?event=%s' % str(event.key()) )
        #except:
        #    return...error
    else:
        c = Context({
                'logouturl':LOGOUT,
                'loginurl':LOGIN,
                'cur_user':CURUSER,
                'is_admin':users.is_current_user_admin(),
                'is_admin':True,
                'event':Event(),
                })
    return render_to_response( 'newevent.htm',c )
        
def edit_event(request):
    if not users.is_current_user_admin():
        return HttpResponseRedirect('/')

    ekey = memcache.get('event')
    event = Event.get(ekey)
    
    if request.method == 'POST':
        event.is_public = request.POST['is_public'] =='1'
        event.title=request.POST['title'].strip()
        event.desc=request.POST['desc'].strip()
        event.put()
        return HttpResponseRedirect( '../event/?event=%s' % str(event.key()) )
    else:
        c = Context({
                  'logouturl':users.create_logout_url('/login'),
                  'is_admin':True,
                  'event':event,
                  })
        return render_to_response( 'newevent.htm',c )
    
def del_event(request):
    if not users.is_current_user_admin():
        return HttpResponseRedirect('/')

    ekey = memcache.get('event')
    memcache.delete('event')
    event = Event.get(ekey)
    # delete sub events
    se_list = Subevent.gql("where event = :1",event)
    db.delete( se_list )
    
    event.delete()
    # delete relate history
    history_li = History.all().filter('event =',event)
    db.delete( history_li )
    
    return HttpResponse("deleted")

def home( request ):
    # get ongoing sub events
    subs = Subevent.all().filter( 'is_done =',False ).filter( 'start_date <=',today() )
    se_list = []
    for se in subs:
        item = {'se':se,
                'days':( se.end_date - today() ).days}
        se_list.append( item )
        
    se_list = sorted(se_list,key=lambda x:x['days'])
    # get recent history operation
    hi_list = History.all().order('-publish_time').fetch(5)
    comments = Comment.all().order('-publish_time').fetch(5)
    # get recent messages
    mes_li = Mes.all().order('-publish_time').fetch(5)

    tip = Tip.all().order('-publish_time').get()
    if tip:
        tip_content = tip.content
    else:
        tip_content = None
    c = Context({
                  'logouturl':users.create_logout_url('/login'),
                  'loginurl':LOGIN,
                  'cur_user':CURUSER,
                  'is_admin':users.is_current_user_admin(),
                  'se_list':se_list,
                  'hi_list':hi_list,
                  'comments':comments,
                  'mes_li':mes_li,
                  'tip':tip_content,
                 })
    return render_to_response('home.htm',c)

def event(request):
    try:
        ekey = request.GET['event']
        # record the current event for further useage
    except KeyError:
        ekey = memcache.get('event')
        if not ekey:
            raise Http404
    
    event = Event.get(Key(ekey))
    memcache.set('event',event.key())

    # get sub event of this event
    se_list = Subevent.gql("where event = :1 order by start_date,end_date",event) 
    # check up wheather sub event is expired
    for se in se_list:
        if se.isexpired==False and se.end_date < today():
            se.isexpired = True
            se.put()
    # get host's history operation on this event
    history_li = History.all().filter('event =',event).order('-publish_time')
    # get blogs about this event
    blog_li = Blog.all().filter('event =',event )
    # get myevents
    myevents = Event.all()
    
    c = Context({
            'logouturl':LOGOUT,
            'loginurl':LOGIN,
            'cur_user':CURUSER,
            'is_admin':users.is_current_user_admin(),
            'event':event,
            'myevents':myevents,
            'se_list':se_list,
            'num_se':se_list.count(20),
            'history_li':history_li,
            'num_history_records':history_li.count(10),
            'blog_li':blog_li,
            'num_blogs':blog_li.count(100),
            })
    return render_to_response('event.htm',c)

def add_sub_event(request):
    if not users.is_current_user_admin():
        return HttpResponseRedirect('/')

    pekey = memcache.get('event')
    if not pekey:
        return render_to_response('error.htm',{'error':'No memcache find,please login again!'})
    pe = Event.get(pekey)
    
    if request.method == 'POST':
        se = Subevent( event=pe,content=request.POST['content'].strip() )
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
        
        if se.end_date < today():
            se.isexpired = True
        else:
            se.isexpired = False
        se.put()
        return HttpResponse( se.key() )
    else:
        return HttpResponse("error")

def edit_sub_event( request ):
    if not users.is_current_user_admin():
        return HttpResponseRedirect('/')

    try:
        sekey = Key(request.POST['key'])
        se = Subevent.get(sekey)
        se.content = request.POST['content']
        pekey = memcache.get('event')
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
    
    if se.end_date < today():
        se.isexpired = True
    else:
        se.isexpired = False
    se.put()
    return HttpResponse( se.isexpired )

def del_sub_event(request):
    if not users.is_current_user_admin():
        return HttpResponseRedirect('/')
    try:
        sekey = Key(request.POST['key'])
        pekey = memcache.get('event')
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

def done_sub_event(request):
    if not users.is_current_user_admin():
        return HttpResponseRedirect('/')
    
    try:
        sekey = Key(request.POST['key'])
        pekey = memcache.get('event')
        is_done = request.POST['is_done']
    except:
        return HttpResponse('error')
    # update event,sub_event,history info
    se = Subevent.get(sekey)
    pe = Event.get(pekey)
    if is_done == 'true':
        se.is_done = True
        se.end_date = today()
        hi = History()
        hi.event = pe
        hi.content = "acomplished:"+se.content
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

def events_list(request):
    events = Event.all().order('start_date')
        
    c = Context({
            'logouturl':LOGOUT,
            'loginurl':LOGIN,
            'cur_user':CURUSER,
            'is_admin':users.is_current_user_admin(),
            'events':events,
            'kind':'all',
            })
    return render_to_response( 'event_list.htm',c)

def events_doing(request):
    events = Event.all().filter( 
        'start_date <=',today() ).filter('is_done =',False ).order('start_date')
        
    c = Context({
                 'events':events,
                 'kind':'doing',
                 'loginurl':LOGIN,
                 'cur_user':CURUSER,
                 'logouturl':LOGOUT,
                 'is_admin':users.is_current_user_admin(),
                 })
    return render_to_response( 'event_list.htm',c)

def events_todo(request):
    events = Event.all().filter( 
        'start_date >',today() ).filter('is_done =',False ).order('start_date')
        
    c = Context({
                 'events':events,
                 'kind':'todo',
                 'loginurl':LOGIN,
                 'cur_user':CURUSER,
                 'logouturl':LOGOUT,
                 'is_admin':users.is_current_user_admin(),
                 })
    return render_to_response( 'event_list.htm',c)

def events_done(request):
    events = Event.all().filter('progress =',100 ).order('-start_date')
        
    c = Context({'events':events,
                 'kind':'done',
                 'loginurl':LOGIN,
                 'cur_user':CURUSER,
                 'logouturl':LOGOUT,
                 'is_admin':users.is_current_user_admin(),
                 })
    return render_to_response( 'event_list.htm',c)
