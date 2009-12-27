#coding=utf-8
from google.appengine.api import memcache
from my_settings import *
import datetime 
from math import ceil

# reset memcache for websites changes
# para:
#     host:User_profile
def reset_memcache( host ):
    memcache.set('hostid',host.uid)
    memcache.set('uname',host.user.nickname())
    memcache.set('headshot',host.headshot)
    memcache.set('rank',host.rank)
    memcache.set('sign',host.sign)

#change UTC time to beijing
def now():
    h = datetime.timedelta(hours=8)
    now = datetime.datetime.now()+h
    return now

#change UTC time to beijing
def today():
    t=datetime.time(0)
    time = datetime.datetime.combine( datetime.date.today(),t )
    h = datetime.timedelta(hours=8)
    now = time+h
    return datetime.date(now.year,now.month,now.day)

#获得get或post参数，如果没有，去默认值value
def http_get( request,name,value ):
    if request.REQUEST.has_key(name):
        return request.REQUEST[name]
    else:
        return value

pages_num =lambda total:ceil(float(total)/PAGE_COUNT)

#统计分页的起始
def page_count(pageid,total):
    offset = pageid*PAGE_COUNT
    next = offset + PAGE_COUNT-1
    if total > next:
        limit = PAGE_COUNT
    else:
        limit = total - offset
    
    if limit < 0:
        offset = 0
        limit =0
        
    return (limit,offset)

