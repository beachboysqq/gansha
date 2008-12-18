# -*- coding: cp936 -*-
from gansha.blog.models import *
from gansha.blog.forms import *
from django.http import HttpResponse
from django.http import HttpResponseRedirect
import datetime, random, sha
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
from django.template import Context, Template


#显示blog，以及comment，没完成
def blog_detail(request):
    try:
        id =request.session['member_id']
    except KeyError:
        return HttpResponse('You have not login,and have no right of accessing!')
    logined =True
    user = User.objects.get(id = id)
    username = user.username
    last_login = user.last_login
    basicInfo = user.userbasicinfo
    achievement = basicInfo.achievement
    signature = basicInfo.signature
    if request.method == 'POST':
        form = EditBlogForm(request.POST)
        if form.is_valid():
            user_id = User.objects.get(id = id)
            blog_id = form.cleaned_data['blog_info']
            olist   = Blog.objects.filter(id = blog_id);
            if(olist.count()>0):
                blog=olist.all()[0]
                title   = form.cleaned_data['title']
                content = form.cleaned_data['content']
                is_author=False
                if(user==blog.user_id):
                    is_author=True
                com_list = Remark.objects.filter(blog_id=blog.id).order_by('id')
                c=Context({"username":username,
                    "headshot":basicInfo.headshot,
                    "achievement":achievement,
                    "signature":signature,
                    "last_login":last_login,
                       "blog_id":blog.id,
                       "blog_title":blog.title,
                       "publish_time":blog.publish_time,
                       "is_author":is_author,
                       "blog_content":blog.content,
                       "comment_number":com_list.count(),
                        "comment_list":com_list,
                    })
                return render_to_response('blogdetail.htm', c)
            else:
                return  HttpResponse('No Blog!')    
    return  HttpResponse('Request method error!!')  

    
#新建一个blog
def new_blog(request,event_id):
    try:
        id =request.session['member_id']
    except KeyError:
        return HttpResponse('You have not login,and have no right of accessing!')
    logined =True
    user = User.objects.get(id = id)
    username = user.username
    last_login = user.last_login
    basicInfo = user.userbasicinfo
    achievement = basicInfo.achievement
    signature = basicInfo.signature    
    is_author = True    
    if request.method == 'POST':
        form = EditBlogForm(request.POST)
        if form.is_valid():
            event_list = Event.objects.filter(id = event_id);
            if event_list.count()>0:
                event_instance = event_list.all()[0]
                title   = form.cleaned_data['title']
                content = form.cleaned_data['content']
                olist   = Blog.objects.filter(title = title);
                #title不能重复
                if olist.count() > 0:
                    error_msg="Title redefination"
                    c = Context({"username":username,
                    "headshot":basicInfo.headshot,
                    "achievement":achievement,
                    "signature":signature,
                    "last_login":last_login,
                     "is_author":is_author,
                     "error_msg":error_msg
                    })
                    return render_to_response('blogissue.htm', c)
                blog = Blog(event_id = event_instance,user_id = user,title = title , content = content)
                publish_time=blog.publish_time
                blog.save()
                com_list=Remark.objects.filter(blog_id=blog.id).order_by('id')
                c=Context({"username":username,
                    "headshot":basicInfo.headshot,
                    "achievement":achievement,
                    "signature":signature,
                    "last_login":last_login,
                       "blog_id":blog.id,
                       "blog_title":title,
                       "publish_time":publish_time,
                       "is_author":is_author,
                       "blog_content":content,
                       "comment_number":com_list.count(),
                        "comment_list":com_list,
                    })
                return render_to_response('blogdetail.htm', c)
            else:
                #event 不存在
                error_msg="Event does not exist!"
                c = Context({"username":username,
                    "headshot":basicInfo.headshot,
                    "achievement":achievement,
                    "signature":signature,
                    "last_login":last_login,
                     "is_author":is_author,
                     "error_msg":error_msg
                    })
                return render_to_response('blogissue.htm', c)
        else:
            #表单错误
            error_msg="Un accessable form!"
            c = Context({"username":username,
                    "headshot":basicInfo.headshot,
                    "achievement":achievement,
                    "signature":signature,
                    "last_login":last_login,
                     "is_author":is_author,
                     "error_msg":error_msg
                    })
            return render_to_response('blogissue.htm', c)

    else:
       #request method =GET
        c = Context({"username":username,
                    "headshot":basicInfo.headshot,
                    "achievement":achievement,
                    "signature":signature,
                    "last_login":last_login,
                     "is_author":is_author
                    })       
        return render_to_response('blogissue.htm', c)
#显示编辑blog页面
def display_edit(request):
    try:
        id =request.session['member_id']
    except KeyError:
        return HttpResponse('You have not login,and have no right of accessing!')
    logined =True
    user = User.objects.get(id = id)
    username = user.username
    last_login = user.last_login
    basicInfo = user.userbasicinfo
    achievement = basicInfo.achievement
    signature = basicInfo.signature
    if request.method=="POST":
        #读取blog.id,event.id
        form = BlogInfo(request.POST)
        if form.is_valid():
            blog_id = form.cleaned_data['blog_info']
            #post_type="old"表示现在的blog不是新的，而是已存在。
            post_type="old"
            olist=Blog.objects.filter(id=blog_id)
            blog = olist.all()[0]
            c = Context({"username":username,
                    "headshot":basicInfo.headshot,
                    "achievement":achievement,
                    "signature":signature,
                    "last_login":last_login,
                    "post_type":post_type,
                     "blog_id":blog.id,
                    "default_title":blog.title,
                    "default_content":blog.content
                    })
            return render_to_response('blogissue.htm', c)
        else:
            return HttpResponse('Form unaccessable!')
    else:
        return HttpResponse('Request method error!!')
#处理编辑blog请求
def edit_blog(request):
    try:
        id =request.session['member_id']
    except KeyError:
        return HttpResponse('You have not login,and have no right of accessing!')
    logined =True
    user = User.objects.get(id = id)
    username = user.username
    last_login = user.last_login
    basicInfo = user.userbasicinfo
    achievement = basicInfo.achievement
    signature = basicInfo.signature   
    if request.method == 'POST':
        form = EditBlogForm(request.POST)
        if form.is_valid():
            user_id = User.objects.get(id = id)
            #event_id = form.cleaned_data[''];
            #publish_time = datetime.datetime.now()
            blog_id = form.cleaned_data['blog_info']
            olist   = Blog.objects.filter(id = blog_id);
            if(olist.count()>0):
                blog=olist.all()[0]
                title   = form.cleaned_data['title']
                content = form.cleaned_data['content']
                blog.title=title
                blog.content=content
                publish_time=datetime.datetime.now()
                blog.publish_time=publish_time
                blog.save()
                blog_id = blog.id
                com_list = Remark.objects.filter(blog_id=blog.id).order_by('id')
                c=Context({"username":username,
                    "headshot":basicInfo.headshot,
                    "achievement":achievement,
                    "signature":signature,
                    "last_login":last_login,
                       "blog_id":blog_id,
                       "blog_title":title,
                       "publish_time":publish_time,
                       "is_author":True,
                       "blog_content":content,
                       "comment_number":com_list.count(),
                        "comment_list":com_list,
                    })
                return render_to_response('blogdetail.htm', c)
            else:
                return  HttpResponse('No Blog!')    
    return  HttpResponse('Request method error!!')    
    
#删除一个blog,同时删除它的所有comment
def delete_blog(request):
    try:
        id =request.session['member_id']
    except KeyError:
        return HttpResponse('You have not login,and have no right of accessing!')
    if request.method=="POST":
        form = BlogInfo(request.POST)
        if form.is_valid():
            blog_id = form.cleaned_data['blog_info']
            olist   = Blog.objects.filter(id = blog_id);
            if(olist.count()>0):
                blog_id=olist.all()[0].id
                olist.delete()
                com_list=Remark.objects.filter(blog_id = blog_id)
                com_list.delete()
                com_list = Remark.objects.filter(blog_id=blog_id).order_by('id')
                if com_list.count()>0:
                    com_list.delete
            else:
                return  HttpResponse('No blog to delete!')
        else:
            return  HttpResponse('Unaccessable form!')
    else:
        return  HttpResponse('Request method error!') 
    logined =True    
    user = User.objects.get(id = id)
    basicInfo = user.userbasicinfo
    event_list = Event.objects.filter( user_id=user )
    c = Context({"username":user.username,
                 "headshot":basicInfo.headshot,
                "achievement":basicInfo.achievement,
                "signature":basicInfo.signature,
                "last_login":user.last_login,
                 'logined':logined,
                 'event_list':event_list,
                 })
    #删除成功
    return render_to_response('home.htm', c)
#增加一个comment
def add_comment(request):
    try:
        id =request.session['member_id']
    except KeyError:
        return HttpResponse('You have not login,and have no right of accessing!')
    logined =True
    user = User.objects.get(id = id)
    username = user.username
    last_login = user.last_login
    basicInfo = user.userbasicinfo
    achievement = basicInfo.achievement
    signature = basicInfo.signature
    if request.method == "POST":
        form = EditRemarkForm(request.POST)
        if form.is_valid():
            blog_id = form.cleaned_data['blog_id']
            com_content = form.cleaned_data['new_content']
            blog_list = Blog.objects.filter(id=blog_id)
            if blog_list.count()>0:
                blog=blog_list.all()[0]
                comment = Remark(blog_id=blog,content=com_content,remarker_id=user)
                comment.save()
                com_list = Remark.objects.filter(blog_id=blog.id).order_by('id')
                c=Context({"username":username,
                    "headshot":basicInfo.headshot,
                    "achievement":achievement,
                    "signature":signature,
                    "last_login":last_login,
                       "blog_id":blog_id,
                       "blog_title":blog.title,
                       "publish_time":blog.publish_time,
                       "is_author":True,
                       "blog_content":blog.content,
                       "comment_number":com_list.count(),
                        "comment_list":com_list,
                    })
                return render_to_response('blogdetail.htm', c)
            else:
                return HttpResponse('Unavailable Blog !!')
        else:
            return HttpResponse('Unavailable Form !!')

    return HttpResponse('Request method error!!')

#删除一个comment
def delete_comment(request):
    try:
        id =request.session['member_id']
    except KeyError:
        return HttpResponse('You have not login,and have no right of accessing!')
    logined =True
    user = User.objects.get(id = id)
    username = user.username
    last_login = user.last_login
    basicInfo = user.userbasicinfo
    achievement = basicInfo.achievement
    signature = basicInfo.signature
    if request.method == "POST":
        form = DelCommentInfo(request.POST)
        if form.is_valid():
            blog_id = form.cleaned_data['blog_id_info']
            com_id = form.cleaned_data['comment_id_info']
            com_list = Remark.objects.filter(id=com_id).order_by('id')
            com_list.delete()
            blog_list = Blog.objects.filter(id=blog_id)
            if blog_list.count()>0:
                blog=blog_list.all()[0]
                com_list = Remark.objects.filter(blog_id=blog.id).order_by('id')
                c=Context({"username":username,
                    "headshot":basicInfo.headshot,
                    "achievement":achievement,
                    "signature":signature,
                    "last_login":last_login,
                       "blog_id":blog_id,
                       "blog_title":blog.title,
                       "publish_time":blog.publish_time,
                       "is_author":True,
                       "blog_content":blog.content,
                       "comment_number":com_list.count(),
                        "comment_list":com_list,
                    })
                return render_to_response('blogdetail.htm', c)
            else:
                return HttpResponse('Unavailable Blog !!')
        else:
            return HttpResponse('Unavailable Form !!')

    return HttpResponse('Request method error!!')

    
        

