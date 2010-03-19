#coding=utf-8
from google.appengine.ext import db
from google.appengine.ext.db import Key
from blog.models import *
from event.models import Event
from util.util import now,http_get,page_count,pages_num

################## 查询 ########################
# 1.总查询
def get_blogs(is_admin):
    if is_admin:
        all_blogs = list(Blog.all().order('-publish_time'))
    else:
        all_blogs = list(Blog.all().filter('is_public =',True).order('-publish_time'))
    return all_blogs

# 2.tag查询
def get_blogs_by_tag( word,is_admin ):
    tag = Tag.all().filter('word =',word ).get()
    bts = BlogTag().all().filter('tag =',tag)
    blogs = [ bt.blog for bt in bts ]
    if not is_admin:
        blogs = [ blog for blog in blogs if blog.is_public ]
    return blogs

def get_tags():
    tags = Tag().all().order('-num')
    return list(tags)

def get_blog_tags( blog ):
    bts = BlogTag().all().filter('blog =',blog)
    tags = []
    for bt in bts:
        if bt.tag and bt.tag.word:
            tags.append( bt.tag )
    return tags

# 3.event查询
def get_events():
    events = Event.all().order('-start_date')
    return events

def get_blogs_by_event( ekey,is_admin ):
    if ekey!='None':
        event = Event.get(Key(ekey))
    else:
        event = None
        temp_blogs = list(Blog.all().order('-publish_time'))
    if is_admin:
        all_blogs = [ blog for blog in temp_blogs if blog.event==event]
    else:
        all_blogs = [ blog for blog in temp_blogs if blog.event==event and blog.is_public ]
    return all_blogs

# 4.month查询
def get_months():
    blogs = Blog.all()
    months = []
    for blog in blogs:
        m = blog.publish_time.strftime("%Y-%m") 
        if m not in months:
            months.append(m)
    return reversed(months)

def get_blogs_by_month( month_str,is_admin ):
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
    if is_admin:
        blogs = Blog.all().filter('publish_time <',month_end).filter('publish_time >=',month_start)
    else:
        blogs = Blog.all().filter('is_public =',True).filter('publish_time <',month_end).filter('publish_time >=',month_start)        
    return blogs

############### 新建blog #############
def new_blog(ekey,title,content,tags_str,is_public):
    blog = Blog()
    if ekey!='None':
        blog.event = Event.get(Key(ekey))
    blog.title = title
    blog.content = content
    blog.publish_time = now()
    blog.is_public = is_public 
    blog.put()
    add_tags( tags_str,blog )
    return blog

def add_tags(tags_str,blog):
    # add tags
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

def update_blog( bkey,ekey,title,is_public,content,tags_str ):
    blog = Blog.get(Key(bkey))
    if ekey!='None':
        blog.event = Event.get(Key(ekey))
    
    blog.title = title
    blog.is_public = is_public
    blog.content = content
    blog.put()
        # update tags
    update_tags( blog,tags_str )

# update tags for old blog
# para:
#     r_tags: received tags from blog author
#     blog: conjucate blog object
def update_tags( blog,tags_str ):
    r_tags = tags_str.split() # tags received from author
    if not r_tags:
        r_tags.append('')
    bts = BlogTag().all().filter('blog =',blog)
    for bt in bts:
        # 没有执行？？？
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

    
def remove_blog( bkey ):
    blog = Blog.get(Key(bkey))
    # delete relate comments
    com_list = Comment.gql("where blog = :1",blog)
    db.delete( com_list )
    
    del_tags( blog )
    blog.delete()

def del_tags( blog ):
    bts = BlogTag().all().filter('blog =',blog)
    for bt in bts:
        bt.tag.num -=1
        if bt.tag.num == 0:
            bt.tag.delete()
        bt.delete()

        
