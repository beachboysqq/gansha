#coding=utf-8
from google.appengine.api import users
from django.http import HttpResponseRedirect,HttpResponse
from django.core import serializers
from django.utils import simplejson
from blog.models import *
from event.models import *
from tip.models import *
from util.util import today
from my_settings import IMPORT_FILE

#not admin,go to blogview,else go to home
def index(request):
    user = users.get_current_user()
    if not user or not users.is_current_user_admin():
        return HttpResponseRedirect('/blogview')
    else:
        return HttpResponseRedirect('/home')

def login(request):
    user = users.get_current_user()
    if not user:
        loginurl = users.create_login_url('/')
        return HttpResponseRedirect(loginurl)
    else:
        return HttpResponseRedirect('/')
    


# export blog and event data
def export_data(request):
    str = ""
    style = "json"
    #Blog export
    blog_str = serializers.serialize(style, Blog.all())
    tag_str = serializers.serialize(style, Tag.all())
    blog_tag_str = serializers.serialize(style, BlogTag.all())
    comment_str = serializers.serialize(style, Comment.all())
    message_str = serializers.serialize(style, Mes.all())
    #event export
    event_str = serializers.serialize(style, Event.all())
    subevent_str = serializers.serialize(style, Subevent.all())
    history_str = serializers.serialize(style, History.all())
    data = {
        'blog':simplejson.loads( blog_str ),
        'tag':simplejson.loads( tag_str ),
        'blog_tag':simplejson.loads( blog_tag_str ),
        'comment':simplejson.loads( comment_str ),
        'message':simplejson.loads( message_str ),
        'event':simplejson.loads( event_str ),
        'subevent':simplejson.loads( subevent_str ),
        'history_tag':simplejson.loads( history_str ),
    }
    #tip export[TODO]
    response = HttpResponse( simplejson.dumps(data) )
    response['Content-Disposition'] = 'attachment; filename="archive_%s.json"' % today()
    response['Content-Type'] ='application/octet-stream'
    return response

# tag需要修改：判断避免重复
def import_data(request):
    try:
        f = open( IMPORT_FILE )
        data = simplejson.loads( f.read() )
        f.close()
    except IOError:
        return HttpResponse("Data file dosn't exsit:import/data.json!")
    #import event
    events = data['event']
    for event in events:
        inevent = Event(key_name=event['pk'],
                        title=event['fields']['title'],
                        desc=event['fields']['desc'],
                        progress=event['fields']['progress'],
                        is_done=event['fields']['is_done'],
                        publish_date=datetime.datetime.strptime(event['fields']['publish_date'],"%Y-%m-%d").date(),
                        start_date=datetime.datetime.strptime(event['fields']['start_date'],"%Y-%m-%d").date(),
                        end_date=datetime.datetime.strptime(event['fields']['end_date'],"%Y-%m-%d").date(),
                        num_se=event['fields']['num_se'])
        inevent.put()
    #subevent import
    ses = data['subevent']
    for se in ses:
        ekey = se['fields']['event']
        event = Event.get_by_key_name(ekey)
        inse = Subevent(event=event,
                  content=se['fields']['content'],
                  start_date=datetime.datetime.strptime(se['fields']['start_date'],"%Y-%m-%d").date(),
                  end_date=datetime.datetime.strptime(se['fields']['end_date'],"%Y-%m-%d").date(),
                  is_done=se['fields']['is_done'],
                  isexpired=se['fields']['isexpired'],
                  )
        inse.put()
    #import blog
    blogs = data['blog']
    for blog in blogs:
        ekey = blog['fields']['event']
        if ekey:
            event = Event.get_by_key_name(ekey)
        else:
            event = None
        inblog = Blog(key_name=blog['pk'],
                      event=event,
                      title=blog['fields']['title'],
                      content=blog['fields']['content'],
                      is_public=True,
                      publish_time=datetime.datetime.strptime(blog['fields']['publish_time'][:-7],"%Y-%m-%d %H:%M:%S"),
                      )
        inblog.put()
    #import tag
    tags = data['tag']
    for tag in tags:
        intag = Tag(key_name=tag['pk'],
                    word=tag['fields']['word'],
                    num=tag['fields']['num'])
        intag.put()
        
    #import blog_tag
    blog_tags = data['blog_tag']
    for blog_tag in blog_tags:
        bkey = blog_tag['fields']['blog']
        tkey = blog_tag['fields']['tag']
        blog = Blog.get_by_key_name(bkey)
        if tkey:
            tag = Tag.get_by_key_name(tkey)
        else:
            tag = None
        inblog_tag = BlogTag( blog=blog,tag=tag )
        inblog_tag.put()
    #import comment
    # comments = data['comment']
    # for comment in comments:
    #     bkey = comment['fields']['blog']
    #     blog = Blog.get_by_key_name(bkey)
    #     incomment = Comment( 
    #         sender=comment['fields']['sender'],
    #         blog=blog,
    #         content=comment['fields']['content'],
    #         publish_time=datetime.datetime.strptime(comment['fields']['publish_time'][:-7],"%Y-%m-%d %H:%M:%S"),
    #         )
    #     incomment.put()
    #import message
    #import history
    #import tips
        
    return HttpResponse( 'ok' )

def repair_tags( request ):
    #消灭blog_tag中的空头
    blog_tags = BlogTag.all()
    for blog_tag in blog_tags:
        try:
            if not blog_tag.blog or not blog_tag.tag:
                blog_tag.delete()
            if not bog_tag.tag.word:
                blog.tag.word = 'notag'
        except:
            blog_tag.delete()
    #修正tag计数
    tags = Tag.all()
    for tag in tags:
        num = 0
        for blog_tag in blog_tags:
            if tag == blog_tag.tag:
                num +=1
                
        tag.num = num
        if tag.num == 0:
            tag.delete()
            
    # 修正一个blog有一个非default的同时，还保留了default tag
    blog_tags = BlogTag.all()
    for bt in blog_tags:
        if bt.tag.word == 'default':
            for bto in blog_tags:
                if bt != bto and bt.blog==bto.blog:
                    bt.tag.num -=1
                    if bt.tag.num == 0:
                        bt.tag.delete()
                        
                    bt.delete()
                    
    return HttpResponse( 'Repair completed:)' )
