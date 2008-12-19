# -*- coding: cp936 -*-
import datetime
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect,HttpResponse
from gansha.settings import MEDIA_URL
from gansha.blog.models import Blog,Comment,Mes
from gansha.blog.forms import *
from gansha.event.models import Event,History
from django.http import Http404
from django.template import Context

def add_blog( request ):
    try:
        id =request.session['member_id']
    except KeyError:
        return HttpResponse('You have not login,and have no right of accessing!')
    logined =True
    user = User.objects.get(id = id)
    event_instance = Event.objects.get( id=request.session['eid'] )
    is_author = True    
    if request.method == 'POST':
        form = EditBlogForm(request.POST)
        if form.is_valid():            
            title   = form.cleaned_data['title']
            content = form.cleaned_data['content']
            olist   = Blog.objects.filter(title = title,event_id=event_instance);
            if olist.count() > 0:
                error_msg="Title redefination"
                c = Context({"username":request.session['username'],
                             "headshot":request.session['headshot'],
                             "achievement":request.session['achievement'],
                             "signature":request.session['signature'],
                             "last_login":request.session['last_login'],
                             "event":event_instance,
                             "is_author":is_author,
                             "error_msg":error_msg
                             })
                return render_to_response('blogissue.htm', c)
            blog = Blog(event_id = event_instance,author = user,title = title , content = content,publish_time=datetime.datetime.now())
            blog.save()
            return HttpResponseRedirect( '../blog/?blog=%d' % blog.id )
        else:
            error_msg="Un accessable form!"
            c = Context({"username":request.session['username'],
                    "headshot":request.session['headshot'],
                    "achievement":request.session['achievement'],
                    "signature":request.session['signature'],
                    "last_login":request.session['last_login'],
                     "event":event_instance,
                     "is_author":is_author,
                     "error_msg":error_msg
                    })
            return render_to_response('blogissue.htm', c)
    else:
       #request method =GET
        c = Context({"username":request.session['username'],
                    "headshot":request.session['headshot'],
                    "achievement":request.session['achievement'],
                    "signature":request.session['signature'],
                    "last_login":request.session['last_login'],
                      "event":event_instance,
                     "is_author":is_author
                    })       
        return render_to_response('blogissue.htm', c)
 

def edit_blog( request ):
    try:
        user_id = request.session['member_id']
        logined = True
    except keyError:
        return HttpResponse('You have not loginned,and have no right of accessing!')     

    ##user has submitted his/her blog changes
    if request.method == 'POST':
        form = EditBlogForm(request.POST)
        if form.is_valid():
            blog_id = form.cleaned_data['blog_info']
            blog = Blog.objects.get( id=blog_id )
            blog.title = form.cleaned_data['title']
            blog.publish_time = datetime.datetime.now()
            #...need a way to realize \r\n with next line
            blog.content = form.cleaned_data['content']            
            blog.save()
            return HttpResponseRedirect( '../blog/?blog=%d' % int(blog.id) )
        else:
              return HttpResponse('POST not ivalid')
    ##user just enter this page to edit a blog
    else:
        blog_id = request.session['blog_id']
        blog = Blog.objects.get( id=blog_id )
        c = Context({"username":request.session['username'],
                    "headshot":request.session['headshot'],
                    "achievement":request.session['achievement'],
                    "signature":request.session['signature'],
                    "last_login":request.session['last_login'],
                      "event":blog.event_id,
                     "blog":blog
                    })       
        return render_to_response('blogissue.htm', c)  

#dispaly blog    
def blog( request ):
    try:
        user_id = request.session['member_id']
        logined = True
    except KeyError:
        return HttpResponse('You have not loginned,and have no right of accessing!')     
    
    try:
        blog_id = request.GET.get("blog")
        request.session['blog_id'] = blog_id
    except KeyError:
        raise Http404
    
    is_author = True
    blog = Blog.objects.get( id=blog_id )
    visitor = User.objects.get(id = user_id)
    if blog.author.id != user_id:
        uid = blog.author.id
        request.session['who'] = uid
        #is_author = False
        ##reset user information for session
        user = User.objects.get(id = uid)
        basicInfo = user.userbasicinfo
        request.session['username'] = user.username
        request.session['headshot'] = MEDIA_URL + str(basicInfo.headshot)
        request.session['achievement'] = basicInfo.achievement
        request.session['signature'] = basicInfo.signature
        request.session['last_login'] = user.last_login 
    ##get comments
    com_list = Comment.objects.filter( blog_id=blog ).order_by('publish_time')
    c = Context({"username":request.session['username'],
                    "headshot":request.session['headshot'],
                    "achievement":request.session['achievement'],
                    "signature":request.session['signature'],
                    "last_login":request.session['last_login'],
                     "is_author":is_author,
                       "blog":blog,
                        "event":blog.event_id,
                       "comment_number":com_list.count(),
                        "comment_list":com_list,
                    })
    return render_to_response('blogdetail.htm', c)
def del_blog(request):
    try:
        id =request.session['member_id']
    except KeyError:
        return HttpResponse('You have not login,and have no right of accessing!')
    
    if request.method=="POST":
        form = BlogInfo(request.POST)
        if form.is_valid():
            blog_id = form.cleaned_data['blog']
            olist   = Blog.objects.filter(id = blog_id);
            event_id = form.cleaned_data['event_info']
            event_instance = Event.objects.filter(id= event_id)
            if(olist.count()>0):                
                com_list=Comment.objects.filter(blog_id = blog_id)
                com_list.delete()
                olist.delete()
                return HttpResponseRedirect( '../event/?event=%d' % int(event_instance.all()[0].id) )
            else:
                return  HttpResponse('No blog to delete!')
        else:
            return  HttpResponse('Unaccessable form!')
    else:
        try:
            blog_id = request.GET.get("blog")
            request.session['blog_id'] = blog_id
        except KeyError:
            raise Http404
        olist   = Blog.objects.filter(id = blog_id);
        if(olist.count()>0):
            event_instance = olist.all()[0].event_id
            com_list=Comment.objects.filter(blog_id = blog_id)
            com_list.delete()
            olist.delete()
            return HttpResponseRedirect( '../event/?event=%d' % int(event_instance.id))
        else:
            return  HttpResponse('No blog to delete!')
   

def add_comment( request ):
    try:
        id =request.session['member_id']
    except KeyError:
        return HttpResponse('You have not login,and have no right of accessing!')
    user = User.objects.get(id = id)
    if request.method == "POST":
        form = EditComForm(request.POST)
        if form.is_valid():
            blog_id = form.cleaned_data['blog_id']
            com_content = form.cleaned_data['new_content']
            blog_list = Blog.objects.filter(id=blog_id)
            if blog_list.count()>0:
                blog=blog_list.all()[0]
                comment = Comment( user_id=blog.author,
                       author=user,
                       blog_id=blog,
                       content= com_content)                
                comment.save()
                return HttpResponseRedirect( '../blog/?blog=%d' % int(blog.id) )
            else:
                return HttpResponse('Unavailable Blog !!')
        else:
            return HttpResponse('Unavailable Form !!')

    return HttpResponse('Request method error!!')
########################################    

    
def del_comment( request ):
    try:
        user_id =request.session['member_id']
    except KeyError:
        return HttpResponse('You have not login,and have no right of accessing!')
    user = User.objects.get(id = user_id)
    if request.method == "POST":
        form = BlogInfo(request.POST)
        if form.is_valid():
            blog_id = form.cleaned_data['blog']
            com_id = form.cleaned_data['com_id']
            com_list = Comment.objects.filter(id=com_id)
            if user == com_list.all()[0].author:
                com_list.delete()
            else:
                if user == Blog.objects.filter(id = blog_id).all()[0].author:
                    com_list.delete()
            return HttpResponseRedirect( '../blog/?blog=%d' % int(blog_id) )
        else:
            return HttpResponse('Unavailable Form !!')
    return HttpResponse('Request method error!!')


def message( request ):
    try:
        user_id = request.session['member_id']
        logined = True
    except KeyError:
        return HttpResponse('You have not loginned,and have no right of accessing!')     
    visitor = User.objects.get( id=user_id )
    
    is_admin = True
    if request.session['who'] != user_id:
        user_id = request.session['who']
        is_admin = False 

    user = User.objects.get( id=user_id )
    mes_li = Mes.objects.filter( receiver=user ).order_by('publish_time')
    c = Context({"username":request.session['username'],
                 "headshot":request.session['headshot'],
                 "achievement":request.session['achievement'],
                 "signature":request.session['signature'],
                 "last_login":request.session['last_login'],
                 'mes_li':mes_li,
                 'visitor':visitor,
                 'logined':logined,
                 'is_admin':is_admin,
                 })
    return render_to_response( 'message.htm',c)


def add_mes( request ):
    sender = User.objects.get( id=request.session['member_id'] )
    receiver = User.objects.get( id=request.session['who'] )
    
    mes = Mes( sender=sender,
               receiver=receiver,
               content=request.POST['content'])
    mes.save()
    return HttpResponse( datetime.datetime.now().strftime("%Y-%m-%d %H:%M") )
    
def del_mes( request ):
    mes = Mes.objects.get( id=request.POST['mid'] )
    mes.delete()
    return HttpResponse( 'deleted' )

