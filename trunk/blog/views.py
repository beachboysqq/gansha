#coding=utf-8
from google.appengine.api import users,memcache
from google.appengine.ext import db
from google.appengine.ext.db import Key
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.template import Context
from django.contrib.auth.decorators import login_required
from userAdmin.models import User_profile
from event.models import Event,History
from blog.models import *
from util.util import now,http_get,page_count,pages_num
import datetime

def get_blog_tags( blog ):
    bts = BlogTag().all().filter('blog =',blog)
    tags = []
    for bt in bts:
        if bt.tag.word:
            tags.append( bt.tag )
    return tags

def get_tag_blogs( tag,user ):
    bts = BlogTag().all().filter('tag =',tag)
    blogs = []
    for bt in bts:
        if bt.blog.author == user:
            blogs.append( bt.blog )
    return blogs

# get users tags
def get_user_tags( user ):
    myblogs = Blog.all().filter('author =',user)
    ret = []
    for blog in myblogs:
        tags = get_blog_tags( blog )
        for tag in tags:
            if tag not in ret:
                ret.append(tag)
    return ret

# add tags for new blog
# para:
#     r_tags: received tags from blog author
#     blog: conjucate blog object
def add_tags( tags_str,blog ):
    r_tags = tags_str.split() # tags received from author
    if not r_tags:
        r_tags.append('')
    # update r_tags to database
    for r_tag in r_tags:
        # update Tag table
        res = Tag().all().filter('word =',r_tag)
        if not res:
            # tag is not exsit before
            tag = Tag()
            tag.word = r_tag
        else:
            tag = res[0]
        tag.num += 1
        tag.put()
     # update BlogTag table
    blog_tag = BlogTag()
    blog_tag.blog = blog
    blog_tag.tag = tag
    blog_tag.put()

# update tags for old blog
# para:
#     r_tags: received tags from blog author
#     blog: conjucate blog object
def update_tags( tags_str,blog ):
    r_tags = tags_str.split() # tags received from author
    if not r_tags:
        r_tags.append('')
    bts = BlogTag().all().filter('blog =',blog)
    for bt in bts:
        if bt.tag.word not in r_tags:
            # old tag not in r_tags,delete bt,if necessary delete tag
            bt.tag.num -=1
            if bt.tag.num == 0:
                bt.tag.delete()
            bt.delete()
        else:
            # old tag in r_tags,remain
            r_tags.remove(bt.tag.word)
    # new tags for blog
    add_tags( ' '.join(r_tags),blog )

# delete tags for a blog
# para:
#     blog: conjucate blog object
def del_tags( blog ):
    bts = BlogTag().all().filter('blog =',blog)
    for bt in bts:
        bt.tag.num -=1
        if bt.tag.num == 0:
            bt.tag.delete()
        bt.delete()

def get_blog_months(user):
    blogs = Blog.all().filter('author =',user)
    months = []
    for blog in blogs:
        m = blog.publish_time.strftime("%Y-%m") 
        if m not in months:
            months.append(m)
    return months

def get_month_blogs( month_str,user ):
    items = month_str.split('-')
    year = int( items[0] )
    month = int( items[1] )
    month_start = datetime.datetime(year,month,1)
    # compute next month 1st
    if month==12:
        month = 1
        year +=1
    else:
        month +=1

    month_end = datetime.datetime(year,month,1)
    blogs = Blog.all().filter('author =',
                              user).filter('publish_time <',month_end).filter('publish_time >=',month_start)
    return blogs
    

def my_events( user ):
    events = Event.all().filter('user =',user)
    return events

# show blogs
def blogview( request ):
    user = users.get_current_user()
    host = User_profile.all().filter('uid =',memcache.get('hostid')).get()
    # reset event key in memcache 
    memcache.set('event','None')
    
    # get recent blogs by tag,event,archive or month
    if request.GET.has_key('tag'):
        view_type = 'tag'
        view_value = request.GET['tag']
        tag = Tag.all().filter('word =',request.GET['tag']).get()
        all_blogs = get_tag_blogs( tag,host.user )
    elif request.GET.has_key('event'):
        view_type = 'event'
        view_value = request.GET['event']
        ekey = request.GET['event']
        if ekey!='None':
            event = Event.get(Key(ekey))
        else:
            event = None
        all_blogs = Blog.all().filter('author =',host.user).filter('event =',event).order('-publish_time')
    elif request.GET.has_key('month'):
        view_type = 'month'
        view_value = request.GET['month']
        month = request.GET['month'].strip()
        all_blogs = get_month_blogs( month,host.user )
    else:
        view_type = None
        view_value = None
        all_blogs = Blog.all().filter('author =',host.user).order('-publish_time')

    #分页
    #tag查询返回的是list，需要特殊处理
    if view_type == 'tag':
        all_num = len(all_blogs)
        pnum = pages_num( all_num )
        pageid = http_get(request,'pageid',0)
        (limit,offset) = page_count( int(pageid),all_num )
        blogs = all_blogs[offset:offset+limit]
    else:
        all_num = all_blogs.count(1000)
        pnum = pages_num( all_num )
        pageid = http_get(request,'pageid',0)
        (limit,offset) = page_count( int(pageid),all_num )
        blogs = all_blogs.fetch(limit,offset)        
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
        ret_blog ={
            'key':str(blog.key()),
            'title':blog.title,
            'time':blog.publish_time,
            'author':blog.author,
            'tags':get_blog_tags( blog ),
            'event':be,
            'com_num':coms.count(1000),
            'brief':blog.content[:160]+"...",
            }
        ret_blogs.append( ret_blog )
    
    # get recent comments
    comments = Comment.all().filter('receiver =',host.user).order('-publish_time').fetch(5)
    
    c = Context({"uname":memcache.get('uname'),
                 "headshot":memcache.get('headshot'),
                 "rank":memcache.get('rank'),
                 "sign":memcache.get('sign'),
                 'logouturl':memcache.get('logouturl'),
                 "last_login":memcache.get('last_login'),
                 'is_admin':user.user_id()==memcache.get('hostid'),
                 "blogs":ret_blogs,
                 "tags":get_user_tags( host.user ), 
                 "events":my_events(host.user),
                'months':get_blog_months(host.user),
                 'comments':comments,
                 'view_type':view_type,
                 'view_value':view_value,
                 'pages_nums':pages_nums,
                 'pageid':int(pageid),
                 })
    return render_to_response('blogview.htm', c)

# show one blog
@login_required
def blog( request ):
    user = users.get_current_user()
    host = User_profile.all().filter('uid =',memcache.get('hostid')).get()
    
    try:
        bkey = request.GET.get("blog")
        blog = Blog.get(Key(bkey))
    except:
        raise Http404
       
    # reset memcache
    if blog.author.user_id() != memcache.get('hostid'):
        host = User_profile.gql('where user = :1',blog.author).get()
        memcache.set('hostid',host.uid)
        memcache.set('uname',blog.author.nickname())
        memcache.set('rank',host.rank)
        memcache.set('sign',host.sign)
        memcache.set('last_login',host.last_login)
        memcache.set('headshot',host.headshot)
    elif blog.event:
        #reset event memcache
        memcache.set('event',blog.event.key())
    # get comments
    comments = Comment.all().filter('blog =',blog).order('publish_time')
    
    c = Context({"uname":memcache.get('uname'),
                 "headshot":memcache.get('headshot'),
                 "rank":memcache.get('rank'),
                 "sign":memcache.get('sign'),
                 'logouturl':memcache.get('logouturl'),
                 "last_login":memcache.get('last_login'),
                 'is_admin':user==blog.author,
                 'visitor':user,
                 "blog":blog,
                 'count':comments.count(),
                 "comments":comments,
                 'blog_tags':get_blog_tags( blog ),
                 "tags":get_user_tags( host.user ),
                 "events":my_events(host.user),
                 'months':get_blog_months(host.user),
                 })
    return render_to_response('blog.htm', c)

@login_required
def add_blog( request ):
    user = users.get_current_user()
    
    if request.method == 'POST':
        blog = Blog()
        blog.author = user
        ekey = request.POST['event_key']
        if ekey!='None':
            blog.event = Event.get(Key(ekey))
        blog.title = request.POST['title'].strip()
        blog.content = request.POST['content'].strip()
        blog.publish_time = now()
        blog.put()
        # add tags
        add_tags( request.POST['tags'].strip(),blog )

        # record in history
        if blog.event:
            hi = History()
            hi.event = blog.event
            hi.content = "add blog:<a href='../blog/?blog="+str(blog.key())+"'>"+blog.title+"</a>"
            hi.user = user
            hi.put()
        return HttpResponseRedirect( '../blog/?blog=%s' % blog.key() )
    else:
       #request method =GET
        c = Context({"uname":memcache.get('uname'),
                     "headshot":memcache.get('headshot'),
                     "rank":memcache.get('rank'),
                     "sign":memcache.get('sign'),
                     'logouturl':memcache.get('logouturl'),
                     "last_login":memcache.get('last_login'),
                     "blog":None,
                     "events":my_events(user),
                     'def_event':memcache.get('event'),
                     "is_admin":True
                     })       
        return render_to_response('blogissue.htm', c)
 
@login_required
def edit_blog( request ):
    user = users.get_current_user()
    # update blog info
    if request.method == 'POST':
        bkey = request.POST['bkey'].strip()
        blog = Blog.get(Key(bkey))
        ekey = request.POST['event_key']
        if ekey!='None':
            blog.event = Event.get(Key(ekey))
        blog.title = request.POST['title'].strip()
        blog.content = request.POST['content'].strip()
        blog.put()
        # update tags
        update_tags( request.POST['tags'].strip(),blog )
        return HttpResponseRedirect( '../blog/?blog=%s' % bkey )
    else:
       # supple the orginal blog info
        bkey = request.GET['blog'].strip()
        blog = Blog.get(Key(bkey))
        tags = get_blog_tags( blog )
        tags_str = ''
        for tag in tags:
            tags_str += str(tag.word)
        c = Context({"uname":memcache.get('uname'),
                     "headshot":memcache.get('headshot'),
                     "rank":memcache.get('rank'),
                     "sign":memcache.get('sign'),
                     'logouturl':memcache.get('logouturl'),
                     "last_login":memcache.get('last_login'),
                     'blog':blog,
                     "events":my_events(user),
                     'def_event':memcache.get('event'),
                     'blog_tags':tags_str,
                     "is_admin":True,
                     })       
        return render_to_response('blogissue.htm', c)

@login_required
def del_blog( request ):
    user = users.get_current_user()
    if not user:
        return render_to_response('error.htm',{'error':'You have not login,and have no right of accessing!'})
    bkey = request.REQUEST['blog']
    blog = Blog.get(Key(bkey))
    ekey = str(blog.event.key())
    # delete relate comments
    com_list = Comment.gql("where blog = :1",blog)
    db.delete( com_list )
    
    del_tags( blog )
    blog.delete()
    return HttpResponse('1')

@login_required
def add_comment( request ):
    bkey = request.POST['bkey']
    blog = Blog.get(Key(bkey))
    
    user = users.get_current_user()
    comment = Comment( receiver=blog.author,
                       sender=user,
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
    user = users.get_current_user()
    host = User_profile.all().filter('uid =',memcache.get('hostid')).get()
    #new message is posted
    if request.method == 'POST' and request.POST['content'].strip():
        mes = Mes( sender=user,
                   receiver=host.user,
                   content=request.POST['content'].strip(),
                   publish_time=now())
        mes.put()

    mes_li = Mes.all().filter('receiver =',host.user).order('-publish_time')
    
    all_num = mes_li.count()
    pnum = pages_num( all_num )
    pageid = http_get(request,'pageid',0)
    (limit,offset) = page_count( int(pageid),all_num )
    mess = mes_li.fetch(limit,offset)
    if pnum>1:
        pages_nums = range(pnum)
    else:
        pages_nums = None

    c = Context({"uname":memcache.get('uname'),
                 "headshot":memcache.get('headshot'),
                 "rank":memcache.get('rank'),
                 "sign":memcache.get('sign'),
                 'logouturl':memcache.get('logouturl'),
                 "last_login":memcache.get('last_login'),
                 'mes_li':reversed(mess),
                 'count':all_num,
                 'visitor':user,
                 'is_admin':user.user_id() == memcache.get('hostid'),
                 'pages_nums':pages_nums,
                 'pageid':int(pageid),
                 'offset':all_num-offset-limit, # the number of 1st
                 })
    return render_to_response( 'message.htm',c)

@login_required
def add_mes( request ):
    sender = users.get_current_user()
    host = User_profile.all().filter('uid =',memcache.get('hostid')).get()
    receiver = host.user
    
    mes = Mes( sender=sender,
               receiver=receiver,
               content=request.POST['content'].strip(),
               publish_time=now())
    mes.put()
    return HttpResponse( now().strftime("%Y-%m-%d %H:%M") )
    
@login_required
def del_mes( request ):
    mkey = Key(request.POST['mkey'])
    mes = Mes.get(mkey)
    mes.delete()
    return HttpResponse( 'deleted' )


