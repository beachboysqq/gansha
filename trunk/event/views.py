# Create your views here.
import datetime
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from gansha.settings import MEDIA_ROOT,MEDIA_URL
from django.http import HttpResponseRedirect,HttpResponse
from gansha.event.forms import EventForm,Sub_eventForm
from gansha.event.models import *
from gansha.blog.models import Blog
from django.http import Http404
from django.template import Context

def add_event( request ):
    try:
        user_id = request.session['member_id']
        logined = True
    except keyError:
        return HttpResponse('You have not loginned,and have no right of accessing!')     

    if request.method == 'POST':
        form = EventForm( request.POST )
        if form.is_valid():
            event = Event()
            event.title = form.cleaned_data['title']
            str = form.cleaned_data['description']
            #...need a way to realize \r\n with next line
            event.description = str
            event.isprivacy = form.cleaned_data['isprivacy']
            event.user_id = User.objects.get( id=user_id )
            event.save()
            return HttpResponseRedirect( '../event/?event=%d' % event.id )
        else:
              return HttpResponse('POST not ivalid')
    else:
        form = EventForm()
    c = Context({"username":request.session['username'],
                 "headshot":request.session['headshot'],
                 "achievement":request.session['achievement'],
                 "signature":request.session['signature'],
                 "last_login":request.session['last_login'],
                 'logined':logined,
                 'eform':form})
    return render_to_response( 'newevent.htm',c )

def edit_event( request ):
    try:
        user_id = request.session['member_id']
        logined = True
    except keyError:
        return HttpResponse('You have not loginned,and have no right of accessing!')     

    ##user has submitted his/her event changes
    if request.method == 'POST':
        form = EventForm( request.POST )
        if form.is_valid():
            event = Event( id=request.session['eid'] )
            event.title = form.cleaned_data['title']
            str = form.cleaned_data['description']
            #...need a way to realize \r\n with next line
            event.description = str
            event.isprivacy = form.cleaned_data['isprivacy']
            event.user_id = User.objects.get( id=user_id )
            event.save()
            return HttpResponseRedirect( '../event/?event=%d' % int(event.id) )
        else:
              return HttpResponse('POST not ivalid')
    ##user just enter this page to edit a event
    else:
        eid = request.session['eid']
        event = Event.objects.get( id=eid )
        form = EventForm( instance=event )
        request.session['eid'] = eid
        c = Context({"username":request.session['username'],
                     "headshot":request.session['headshot'],
                     "achievement":request.session['achievement'],
                     "signature":request.session['signature'],
                     "last_login":request.session['last_login'],
                     'logined':logined,
                     'eform':form})
        return render_to_response( 'newevent.htm',c )    

#display event and subevent and so on
def event( request ):
    try:
        user_id = request.session['member_id']
        logined = True
    except KeyError:
        return HttpResponse('You have not loginned,and have no right of accessing!')     
    
    try:
        event_id = request.GET.get("event")
    except KeyError:
        raise Http404
        
    event = Event.objects.get( id=event_id )
    request.session['eid'] = event_id
    se_list = Sub_event.objects.filter( event_id=event ).order_by('start_date','end_date')
    ##get user's history operation on this event
    history_li = History.objects.filter( event_id=event_id )
    ##get blog
    blog_li = Blog.objects.filter( event_id=event_id )
    c = Context({"username":request.session['username'],
                 "headshot":request.session['headshot'],
                 "achievement":request.session['achievement'],
                 "signature":request.session['signature'],
                 "last_login":request.session['last_login'],
                 'logined':logined,
                 'event':event,
                 'se_list':se_list,
                 'history_li':history_li,
                 'blog_li':blog_li,})
    return render_to_response( 'event.htm',c)

##add a sub event for this event by ajax way
def add_sub_event( request ):
    se = Sub_event()
    pe = Event.objects.get( id=request.POST['event_id'])
    se.event_id = pe
    se.content = request.POST['content']
    start_date = request.POST['start_date']
    li = start_date.split('-')
    se.start_date = datetime.date( int(li[0]),int(li[1]),int(li[2]))

    end_date = request.POST['end_date']
    li = end_date.split('-')
    se.end_date = datetime.date( int(li[0]),int(li[1]),int(li[2]))
    #adjust the parent event's start_date and end_date
    if se.start_date < pe.start_date:
        pe.start_date = se.start_date
    if se.end_date > pe.end_date:
        pe.end_date = se.end_date
    #adjust progress of parent event,mutipled by 100
    pe.num_se +=1
    pe.progress = pe.progress*(pe.num_se-1)/pe.num_se
    pe.save()
   
    se.isdone = False
    if se.end_date < datetime.date.today():
        se.isexpired = True
    
    se.save()
    return HttpResponse( se.id )

##edit a sub event by ajax way
def edit_sub_event( request ):
    se = Sub_event.objects.get( id=request.POST['id'])
    se.content = request.POST['content']
    
    start_date = request.POST['start_date']
    li = start_date.split('-')
    se.start_date = datetime.date( int(li[0]),int(li[1]),int(li[2]))

    end_date = request.POST['end_date']
    li = end_date.split('-')
    se.end_date = datetime.date( int(li[0]),int(li[1]),int(li[2]))
    #adjust the parent event's start_date and end_date
    pe = se.event_id
    if se.start_date < pe.start_date:
        pe.start_date = se.start_date
    if se.end_date > pe.end_date:
        pe.end_date = se.end_date
    pe.save()
    
    if se.end_date < datetime.date.today():
        se.isexpired = True
    se.save()
    return HttpResponse( se.id )

def del_sub_event( request ):
    se_id = request.POST['id']
    se = Sub_event.objects.get( id=se_id )
    #adjust parent event
    pe = se.event_id
    pe.num_se -=1
    pe.progress = pe.progress*(pe.num_se+1)/pe.num_se
    if pe.start_date == se.start_date:
        pe.start_date = Sub_event.objects.order_by('start_date')[1].start_date
    if pe.end_date == se.end_date:
        pe.end_date = Sub_event.objects.order_by('-end_date')[1].end_date
    pe.save()
    se.delete()
    return HttpResponse( se_id )

##user select the checkbox meanings he/she has done this sub event
##if he/she unselect the checkbox,meanings it has not been acomplished
def done_sub_event( request ):
    se = Sub_event.objects.get( id=request.POST['id'] )
    if request.POST['isdone']=='true':
        se.isdone = True
        hi = History()
        hi.event_id = se.event_id
        hi.content = "acomplished:"+se.content
        hi.user_id = hi.event_id.user_id
        hi.save()
        #adjust parent event's progress
        pe =se.event_id
        pe.progress = pe.progress+100/pe.num_se
        pe.save()
    else:
        se.isdone = False
    se.save()   
    return HttpResponse( se.id )

##show the events doing now
def events_doing( request ):
    try:
        user_id = request.session['member_id']
        logined = True
    except KeyError:
        return HttpResponse('You have not loginned,and have no right of accessing!')     

    user = User.objects.get( id=user_id )
    events = Event.objects.filter( user_id=user ).filter( 
        start_date__lte=datetime.date.today() ).filter(
        progress__lt=100 ).order_by('publish_date')

    c = Context({"username":request.session['username'],
                 "headshot":request.session['headshot'],
                 "achievement":request.session['achievement'],
                 "signature":request.session['signature'],
                 "last_login":request.session['last_login'],
                 'logined':logined,
                 'events':events,
                 'kind':'doing',})
    return render_to_response( 'event_list.htm',c)
##show the events to do

##show the events doing now
def events_todo( request ):
    try:
        user_id = request.session['member_id']
        logined = True
    except KeyError:
        return HttpResponse('You have not loginned,and have no right of accessing!')     

    user = User.objects.get( id=user_id )
    events = Event.objects.filter( user_id=user ).filter( 
        start_date__gt=datetime.date.today() ).order_by('publish_date')

    c = Context({"username":request.session['username'],
                 "headshot":request.session['headshot'],
                 "achievement":request.session['achievement'],
                 "signature":request.session['signature'],
                 "last_login":request.session['last_login'],
                 'logined':logined,
                 'events':events,
                 'kind':
                     'todo'})
    return render_to_response( 'event_list.htm',c)
##show the events has been done
def events_done( request ):
    try:
        user_id = request.session['member_id']
        logined = True
    except KeyError:
        return HttpResponse('You have not loginned,and have no right of accessing!')     

    user = User.objects.get( id=user_id )
    events = Event.objects.filter( user_id=user ).filter( 
        progress=100 ).order_by('publish_date')

    c = Context({"username":request.session['username'],
                 "headshot":request.session['headshot'],
                 "achievement":request.session['achievement'],
                 "signature":request.session['signature'],
                 "last_login":request.session['last_login'],
                 'logined':logined,
                 'events':events,
                 'kind':'done'})
    return render_to_response( 'event_list.htm',c)
##just for test ajax,for there is no better way to display errors with ajax
def test( request ):
    if request.method == 'POST':
        se = Sub_event()
       # se.event_id = Event.objects.get( id=request.POST['event_id'])
        se.content = request.POST['content']
        se.start_date = request.POST['start_date']
        se.end_date = request.POST['end_date']
        se.isdone = False
        li = se.end_date.split('-')
        if datetime.date( int(li[0]),int(li[1]),int(li[2])) < datetime.date.today():
            se.isexpired = True
            return HttpResponse('good')
        return HttpResponse('bad')
    return render_to_response( 'test.html')
