import datetime
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect,HttpResponse
from gansha.settings import MEDIA_URL
from gansha.blog.models import Blog,Comment,Mes
from gansha.blog.forms import BlogForm,CommentForm,MesForm
from gansha.event.models import Event,History
from django.http import Http404
from django.template import Context

def add_blog( request ):
    try:
        user_id = request.session['member_id']
        logined = True
        is_admin = True
    except keyError:
        return HttpResponse('You have not loginned,and have no right of accessing!')     

    if request.method == 'POST':
        #form = BlogForm( request.POST )
       # if form.is_valid():
        blog = Blog()
        blog.event_id = Event.objects.get( id=request.session['eid'] )
        blog.title = request.POST['title']
        #...need a way to realize \r\n with next line
        blog.content = request.POST['content']
        blog.author = User.objects.get( id=user_id )
        blog.save()
        #add to history
        hi = History()
        hi.event_id = blog.event_id
        hi.user_id = hi.event_id.user_id
        hi.content = "add blog:"+blog.title
        hi.save()
        return HttpResponseRedirect( '../blog/?blog=%d' % blog.id )
        #else:
         #     return HttpResponse('POST not ivalid')
    else:
        form = BlogForm()
    c = Context({"username":request.session['username'],
                 "headshot":request.session['headshot'],
                 "achievement":request.session['achievement'],
                 "signature":request.session['signature'],
                 "last_login":request.session['last_login'],
                 'logined':logined,
                 'is_admin':is_admin,
                 'form':form})
    return render_to_response( 'newblog.htm',c )

def edit_blog( request ):
    try:
        user_id = request.session['member_id']
        logined = True
    except keyError:
        return HttpResponse('You have not loginned,and have no right of accessing!')     

    ##user has submitted his/her blog changes
    if request.method == 'POST':
        form = BlogForm( request.POST )
        if form.is_valid():
            blog = Blog.objects.get( id=request.session['blog_id'] )
            blog.title = form.cleaned_data['title']
            #...need a way to realize \r\n with next line
            blog.content = form.cleaned_data['content']
            blog.author = User.objects.get( id=user_id )
            blog.save()
            return HttpResponseRedirect( '../blog/?blog=%d' % int(blog.id) )
        else:
              return HttpResponse('POST not ivalid')
    ##user just enter this page to edit a blog
    else:
        blog_id = request.session['blog_id']
        blog = Blog.objects.get( id=blog_id )
        form = BlogForm( instance=blog )
  
        c = Context({"username":request.session['username'],
                     "headshot":request.session['headshot'],
                     "achievement":request.session['achievement'],
                     "signature":request.session['signature'],
                     "last_login":request.session['last_login'],
                     'logined':logined,
                     'is_admin':True,
                     'form':form,
                     'event_id':request.session['eid'],})
        return render_to_response( 'newblog.htm',c )    

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
    
    is_admin = True
    blog = Blog.objects.get( id=blog_id )
    visitor = User.objects.get(id = user_id)
    if blog.author.id != user_id:
        uid = blog.author.id
        request.session['who'] = uid
        is_admin = False
        ##reset user information for session
        user = User.objects.get(id = uid)
        basicInfo = user.userbasicinfo
        request.session['username'] = user.username
        request.session['headshot'] = MEDIA_URL + str(basicInfo.headshot)
        request.session['achievement'] = basicInfo.achievement
        request.session['signature'] = basicInfo.signature
        request.session['last_login'] = user.last_login 
    ##get comments
    comments = Comment.objects.filter( blog_id=blog ).order_by('publish_time')
    c = Context({"username":request.session['username'],
                 "headshot":request.session['headshot'],
                 "achievement":request.session['achievement'],
                 "signature":request.session['signature'],
                 "last_login":request.session['last_login'],
                 'logined':logined,
                 'blog':blog,
                 'is_admin':is_admin,
                 'visitor':visitor,
                 'comments':comments,
                 })
    return render_to_response( 'blog.htm',c)

def add_comment( request ):
    post_blog = Blog.objects.get( id=request.POST['bid'] )
    user = User.objects.get( id=request.session['member_id'] )
    comment = Comment( user_id=post_blog.author,
                       author=user,
                       blog_id=post_blog,
                       content=request.POST['content'])
    comment.save()
    return HttpResponse( datetime.datetime.now().strftime("%Y-%m-%d %H:%M") )
    
def del_comment( request ):
    comment = Comment.objects.get( id=request.POST['cid'] )
    comment.delete()
    return HttpResponse( 'deleted' )

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

