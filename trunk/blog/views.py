# -*- coding: cp936 -*-
from gansha.blog.models import *
from gansha.blog.forms import *
from django.http import HttpResponse
from django.http import HttpResponseRedirect
import datetime, random, sha
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
from django.template import Context, Template



def blog_detail(request):
    if request.method == 'GET':

        try:
            id =request.session['member_id']
        except KeyError:
            return HttpResponse('You have not login,and have no right of accessing!')
        logined =True
        
        user = User.objects.get(id = id)

        username = user.username
        last_login = user.last_login
                #basicInfo = UserBasicInfo.objects.filter(username = id)
        basicInfo = user.userbasicinfo
        achievement = basicInfo.achievement
        signature = basicInfo.signature
        
        c = Context({"username":username,
                    "headshot":basicInfo.headshot,
                    "achievement":achievement,
                    "signature":signature,
                    "last_login":last_login
                    })

    else:
        return HttpResponse('ERROR Request!')
    return render_to_response('blogdetail.htm', c)

def blog_edit(request):
    try:
        id =request.session['member_id']
    except KeyError:
        return HttpResponse('You have not login,and have no right of accessing!')
    logined =True
    user = User.objects.get(id = id)
    username = user.username
    last_login = user.last_login
        #basicInfo = UserBasicInfo.objects.filter(username = id)
    basicInfo = user.userbasicinfo
    achievement = basicInfo.achievement
    signature = basicInfo.signature    

    is_author = True
    
    if request.method == 'POST':
        form = EditBlogForm(request.POST)
        if form.is_valid():
            user_id = User.objects.get(id = id)
            #event_id = Event();
            #publish_time = datetime.datetime.now()
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            
            olist=Blog.objects.filter(title = title);
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
            else:
                #title = "abc"
                #content = "askldjfalskjdddddadfa"
                #event_id = event_id,
                blog = Blog(user_id = user_id,title = title , content = content)
                publish_time=blog.publish_time
                blog.save()
                c=Context({"username":username,
                    "headshot":basicInfo.headshot,
                    "achievement":achievement,
                    "signature":signature,
                    "last_login":last_login,
                       "blog_title":title,
                       "publish_time":publish_time,
                       "is_author":is_author,
                       "blog_content":content
                    })
                return render_to_response('blogdetail.htm', c)
        else:
            #time_now=datetime.datetime.now
            c = Context({"username":username,
                    "headshot":basicInfo.headshot,
                    "achievement":achievement,
                    "signature":signature,
                    "last_login":last_login,
                    "is_author":is_author
                    #"publish_time":time_now
                    })
            return render_to_response('blogdetail.htm', c)

    else:
        
        c = Context({"username":username,
                    "headshot":basicInfo.headshot,
                    "achievement":achievement,
                    "signature":signature,
                    "last_login":last_login,
                     "is_author":is_author
                    })       
        return render_to_response('blogissue.htm', c)


