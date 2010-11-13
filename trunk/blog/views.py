#coding=utf-8
from google.appengine.api import memcache
from google.appengine.ext.db import Key
from django.shortcuts import render_to_response,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.contrib.auth.decorators import login_required
from django.template import Context
from blog.control import *
from event.models import History
from my_settings import *
from blog.models import *
from util.util import now,http_get,page_count,pages_num

#提供四种查询方式：总查询，Tag查询，事件查询,月份查询
def blogview( request ):
    is_admin = users.is_current_user_admin()
    # get recent blogs by tag,event,archive or month
    if request.GET.has_key('tag'):
        word = request.GET['tag']
        tip = "Tag:%s" % word
        all_blogs = get_blogs_by_tag( word,is_admin )
    elif request.GET.has_key('event'):
        ekey = request.GET['event']
        if ekey!='None':
            event = Event.get(Key(ekey))
            tip = "Event:%s" % event.title        
        else:
            event = None
            tip = "Event:None"      

        all_blogs = get_blogs_by_event( event,is_admin )
    elif request.GET.has_key('month'):
        month = request.GET['month'].strip()
        tip = "Month:%s" % month
        all_blogs = get_blogs_by_month( month,is_admin )
    else:
        tip = "All"
        all_blogs = get_blogs(is_admin)
        
    #分页,并获取指定分页的blog
    all_num = len(all_blogs)
    pnum = pages_num( all_num )
    pageid = http_get(request,'pageid',0)
    (limit,offset) = page_count( int(pageid),all_num )
    blogs = all_blogs[offset:offset+limit]
    if pnum>1:
        pages_nums = range(pnum)
    else:
        pages_nums = None
    
    #blog attributes:title,publish time,author,tags,events,com_num,brief
    ret_blogs = []
    for blog in blogs:
        coms = Comment().all().filter('blog =',blog)       
        if blog.event:
            be = blog.event
        else:
            be = None
        if len(blog.content) > 160:
            brief = blog.content[:160].strip()+"..."
        else:
            brief = blog.content
        ret_blog ={
            'key':str(blog.key()),
            'title':blog.title,
            'time':blog.publish_time,
            'is_public':blog.is_public,
            'tags':get_blog_tags( blog ),
            'event':be,
            'com_num':coms.count(1000),
            'brief':brief,
            }
        ret_blogs.append( ret_blog )

    # get recent comments
    comments = Comment.all().order('-publish_time').fetch(5)
    
    c = Context({
                 "blogs":ret_blogs,
                 'tip':tip,
                 'num':all_num,
                 "tags":get_tags(), 
                 "events":get_events(),
                 'months':get_months(),
                 'comments':comments,
                 'pages_nums':pages_nums,
                 'pageid':int(pageid),
                 'logouturl':LOGOUT,
                 'loginurl':LOGIN,
                 'cur_user':CURUSER,
                 'is_admin':users.is_current_user_admin(),
                 })
    return render_to_response('blogview.htm', c)


#在app.yaml中设定权限认证
def add_blog( request ):
    if not users.is_current_user_admin():
        return HttpResponseRedirect('/blogview')

    if request.method == 'POST':
        ekey = request.POST['event_key']
        title = request.POST['title'].strip()
        is_public = (request.POST['is_public'] == '1')
        content = request.POST['content'].strip()
        tags = request.POST['tags'].strip()
        blog = new_blog( ekey,title,content,tags,is_public )

        # record in history
        if blog.event:
            hi = History()
            hi.event = blog.event
            hi.content = "add blog:<a href='../blog/?blog="+str(blog.key())+"'>"+blog.title+"</a>"
            hi.put()
        return HttpResponseRedirect( '../blog/?blog=%s' % blog.key() )
    else:
       #request method =GET
        c = Context({
                     "blog":None,
                     "events":get_events(),
                     'def_event':memcache.get('event'),
                     "is_admin":True,
                     'logouturl':LOGOUT,
                     'loginurl':LOGIN,
                     'cur_user':CURUSER,
                     })       
        return render_to_response('blogissue.htm', c)

    
def blog( request ):
    bkey = request.GET.get("blog")
    blog = Blog.get(Key(bkey))
       
    # get comments
    comments = Comment.all().filter('blog =',blog).order('publish_time')
    
    c = Context({
            'is_admin':users.is_current_user_admin(),
            'logouturl':LOGOUT,
            'cur_user':CURUSER,
            "blog":blog,
            'count':comments.count(),
            "comments":comments,
            'blog_tags':get_blog_tags( blog ),
            "tags":get_tags(),
            "events":get_events(),
            'months':get_months(),
            'loginurl':LOGIN,
            'cur_user':CURUSER,
                 })
    return render_to_response('blog.htm', c)

def edit_blog( request ):
    if not users.is_current_user_admin():
        return HttpResponseRedirect('/blogview')

    # update blog info
    if request.method == 'POST':
        bkey = request.POST['bkey'].strip()
        blog = Blog.get(Key(bkey))
        ekey = request.POST['event_key']
        title = request.POST['title'].strip()
        is_public = request.POST['is_public'] =='1'
        content = request.POST['content'].strip()
        tags_str = request.POST['tags'].strip()
        update_blog( bkey,ekey,title,is_public,content,tags_str)
        return HttpResponseRedirect( '../blog/?blog=%s' % bkey )
    else:
       # supple the orginal blog info
        bkey = request.GET['blog'].strip()
        blog = Blog.get(Key(bkey))
        tags = get_blog_tags( blog )
        tags_str = ''
        for tag in tags:
            tags_str += (" "+ tag.word)
        if blog.event:
            def_event = blog.event.key()
        else:
            def_event = None
        c = Context({
                'is_admin':True,
                'loginout':LOGOUT,
                'loginurl':LOGIN,
                'cur_user':CURUSER,
                'blog':blog,
                "events":get_events(),
                'def_event':def_event,
                'blog_tags':tags_str,
                "is_admin":True,
                })       
        return render_to_response('blogissue.htm', c)
    
def del_blog( request ):
    if not users.is_current_user_admin():
        return HttpResponseRedirect('/blogview')
    
    bkey = request.REQUEST['blog']
    remove_blog( bkey )
    return HttpResponse('1')


@login_required
def add_comment( request ):
    bkey = request.POST['bkey']
    blog = Blog.get(Key(bkey))
    sender = request.POST['sender'].strip()

    comment = Comment( #sender=CURUSER,
        sender=sender,
        blog=blog,
        content=request.POST['content'].strip(),
        publish_time=now())
    comment.put()
    return HttpResponse( now().strftime("%Y-%m-%d %H:%M") )
    
@login_required
def del_comment( request ):
    comment = Comment.get( Key(request.POST['ckey']) )
    comment.delete()
    return HttpResponse( 'deleted' )


def message( request ):
    #new message is posted
    if request.method == 'POST' and request.POST['content'].strip():
        mes = Mes( sender=CURUSER,
                   content=request.POST['content'].strip(),
                   publish_time=now())
        mes.put()

    mes_li = Mes.all().order('-publish_time')
    
    all_num = mes_li.count()
    pnum = pages_num( all_num )
    pageid = http_get(request,'pageid',0)
    (limit,offset) = page_count( int(pageid),all_num )
    mess = mes_li.fetch(limit,offset)
    if pnum>1:
        pages_nums = range(pnum)
    else:
        pages_nums = None

    c = Context({
                 'logouturl':LOGOUT,
                 'is_admin':users.is_current_user_admin(),
                 'mes_li':reversed(mess),
                 'count':all_num,
                 'pages_nums':pages_nums,
                 'pageid':int(pageid),
                 'cur_user':CURUSER,
                 'offset':all_num-offset-limit, # the number of 1st
                 'loginurl':LOGIN,
                 'cur_user':CURUSER,
                 })
    return render_to_response( 'message.htm',c)

def add_mes( request ):
    if not users.is_current_user_admin():
        return HttpResponseRedirect('/')
    sender = users.get_current_user()
#    sender = request.POST['sender'].strip()
    mes = Mes( sender=sender,
               content=request.POST['content'].strip(),
               publish_time=now())
    mes.put()
    return HttpResponse( now().strftime("%Y-%m-%d %H:%M") )
    
def del_mes( request ):
    if not users.is_current_user_admin():
        return HttpResponseRedirect('/')
    mkey = Key(request.POST['mkey'])
    mes = Mes.get(mkey)
    mes.delete()
    return HttpResponse( 'deleted' )


def note( request ):
    #new message is posted
    if request.method == 'POST' and request.POST['content'].strip():
        note = Note( content=request.POST['content'].strip(),
                   publish_time=now())
        note.put()

    note_li = Note.all().order('-publish_time')
    
    all_num = note_li.count()
    pnum = pages_num( all_num )
    pageid = http_get(request,'pageid',0)
    (limit,offset) = page_count( int(pageid),all_num )
    notes = note_li.fetch(limit,offset)
    if pnum>1:
        pages_nums = range(pnum)
    else:
        pages_nums = None

    c = Context({
                 'logouturl':LOGOUT,
                 'is_admin':users.is_current_user_admin(),
                 'note_li':reversed(notes),
                 'count':all_num,
                 'pages_nums':pages_nums,
                 'pageid':int(pageid),
                 'cur_user':CURUSER,
                 'offset':all_num-offset-limit, # the number of 1st
                 'loginurl':LOGIN,
                 'cur_user':CURUSER,
                 })
    return render_to_response( 'note.htm',c)

def add_note( request ):
    if not users.is_current_user_admin():
        return HttpResponseRedirect('/')
    
    mes = Note( 
               content=request.POST['content'].strip(),
               publish_time=now())
    mes.put()
    return HttpResponse( now().strftime("%Y-%m-%d %H:%M") )
    
def del_note( request ):
    if not users.is_current_user_admin():
        return HttpResponseRedirect('/')
    mkey = Key(request.POST['mkey'])
    mes = Note.get(mkey)
    mes.delete()
    return HttpResponse( 'deleted' )
