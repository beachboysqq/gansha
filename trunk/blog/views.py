import datetime
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect,HttpResponse
from gansha.blog.models import Blog,Comment,Mes
from gansha.blog.forms import BlogForm,CommentForm,MesForm
from gansha.event.models import Event,History
from django.http import Http404
from django.template import Context

def add_blog( request ):
    try:
        user_id = request.session['member_id']
        logined = True
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
        blog_id = int( request.GET.get("blog") )
        request.session['blog_id'] = blog_id
    except KeyError:
        raise Http404
        
    blog = Blog.objects.get( id=blog_id )
    c = Context({"username":request.session['username'],
                 "headshot":request.session['headshot'],
                 "achievement":request.session['achievement'],
                 "signature":request.session['signature'],
                 "last_login":request.session['last_login'],
                 'logined':logined,
                 'blog':blog,
                   'event_id':request.session['eid'],})
    return render_to_response( 'blog.htm',c)
