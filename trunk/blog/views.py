from google.appengine.api import users,memcache
from google.appengine.ext.db import Key
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.template import Context
from userAdmin.models import User_profile
from event.models import Event,Sub_event,History
from blog.models import Blog,Comment,Mes
import datetime

def add_blog( request ):
    user = users.get_current_user()
    if not user:
        return render_to_response('error.htm',{'error':'You have not login,and have no right of accessing!'})
    
    # get the related event
    ekey = memcache.get('event')
    event = Event.get(Key(ekey))
     
    if request.method == 'POST':
        blog = Blog()
        blog.author = user
        blog.event = event
        blog.title = request.POST['title']
        blog.content = request.POST['content']
        blog.put()
        # record in history
        hi = History()
        hi.event = event
        hi.content = "add blog:"+blog.title+" on event:"+event.title
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
                     'event':event,
                     "is_admin":True
                     })       
        return render_to_response('blogissue.htm', c)
 
def blog( request ):
    user = users.get_current_user()
    if not user:
        return render_to_response('error.htm',{'error':'You have not login,and have no right of accessing!'})
        
    try:
        bkey = request.GET.get("blog")
        blog = Blog.get(Key(bkey))
    except:
        raise Http404
    if user == blog.author:
        is_admin = True
    else:
        is_admin = False

    # reset memcache
    if blog.author != users.User(memcache.get('host_email')):
        m_user = User_profile.gql('where user = :1',blog.author).get()
        memcache.set('host_email',blog.author.email())
        memcache.set('uname',blog.author.nickname())
        memcache.set('rank',m_user.rank)
        memcache.set('sign',m_user.sign)
        memcache.set('last_login',m_user.last_login)
        memcache.set('headshot',m_user.headshot)
    # get comments
    comments = Comment.all().filter('blog =',blog).order('publish_time')
    c = Context({"uname":memcache.get('uname'),
                 "headshot":memcache.get('headshot'),
                 "rank":memcache.get('rank'),
                 "sign":memcache.get('sign'),
                 'logouturl':memcache.get('logouturl'),
                 "last_login":memcache.get('last_login'),
                 'is_admin':is_admin,
                 'visitor':user,
                 "blog":blog,
                 'count':comments.count(),
                 "comments":comments,
                 })
    return render_to_response('blog.htm', c)

def edit_blog( request ):
    user = users.get_current_user()
    if not user:
        return render_to_response('error.htm',{'error':'You have not login,and have no right of accessing!'})
        
    # update blog info
    if request.method == 'POST':
        bkey = request.POST['bkey']
        blog = Blog.get(Key(bkey))
        blog.title = request.POST['title']
        blog.content = request.POST['content']
        blog.put()
        return HttpResponseRedirect( '../blog/?blog=%s' % bkey )
    else:
       # supple the orginal blog info
        bkey = request.GET['blog']
        blog = Blog.get(Key(bkey))
        c = Context({"uname":memcache.get('uname'),
                     "headshot":memcache.get('headshot'),
                     "rank":memcache.get('rank'),
                     "sign":memcache.get('sign'),
                     'logouturl':memcache.get('logouturl'),
                     "last_login":memcache.get('last_login'),
                     'blog':blog,
                     "is_admin":True,
                     })       
        return render_to_response('blogissue.htm', c)

def del_blog( request ):
    user = users.get_current_user()
    if not user:
        return render_to_response('error.htm',{'error':'You have not login,and have no right of accessing!'})

    bkey = request.GET['blog']
    blog = Blog.get(Key(bkey))
    ekey = str(blog.event.key())
    blog.delete()
    return HttpResponseRedirect( '../event/?event=%s' % ekey)

def add_comment( request ):
    bkey = request.POST['bkey']
    blog = Blog.get(Key(bkey))
    
    user = users.get_current_user()
    comment = Comment( receiver=blog.author,
                       sender=user,
                       blog=blog,
                       content=request.POST['content'])
    comment.put()
    return HttpResponse( datetime.datetime.now().strftime("%Y-%m-%d %H:%M") )
    
def del_comment( request ):
    comment = Comment.get( Key(request.POST['ckey']) )
    comment.delete()
    return HttpResponse( 'deleted' )

def message( request ):
    user = users.get_current_user()
    if not user:
        return render_to_response('error.htm',{'error':'You have not login,and have no right of accessing!'})
    
    host = memcache.get('host_email')
    host_user = users.User(host)
    if host_user == user:
        is_admin = True
    else:
        is_admin = False

    mes_li = Mes.all().filter('receiver =',host_user ).order('publish_time')
    c = Context({"uname":memcache.get('uname'),
                 "headshot":memcache.get('headshot'),
                 "rank":memcache.get('rank'),
                 "sign":memcache.get('sign'),
                 'logouturl':memcache.get('logouturl'),
                 "last_login":memcache.get('last_login'),
                 'mes_li':mes_li,
                 'count':mes_li.count(),
                 'visitor':user,
                 'is_admin':is_admin,
                 })
    return render_to_response( 'message.htm',c)

def add_mes( request ):
    sender = users.get_current_user()
    host = memcache.get('host_email')
    receiver = users.User(host)
    
    mes = Mes( sender=sender,
               receiver=receiver,
               content=request.POST['content'])
    mes.put()
    return HttpResponse( datetime.datetime.now().strftime("%Y-%m-%d %H:%M") )
    
def del_mes( request ):
    mkey = Key(request.POST['mkey'])
    mes = Mes.get(mkey)
    mes.delete()
    return HttpResponse( 'deleted' )


