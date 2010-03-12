# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _
from google.appengine.ext.db import Key
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.shortcuts import render_to_response
from util.util import now,http_get,page_count,pages_num
from my_settings import *
from tip.models import Tip

def add_tip(request):
    if not users.is_current_user_admin():
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        tip = Tip( content=request.POST['content'].strip(),
                   publish_time=now() )
        tip.put()        
        return HttpResponse( tip.content )
    else:
        return HttpResponse("error")

def tips( request ):
    tips = Tip.all().order('-publish_time')

    all_num = tips.count(1000)
    pnum = pages_num( all_num )
    pageid = http_get(request,'pageid',0)
    (limit,offset) = page_count( int(pageid),all_num )
    mess = tips.fetch(limit,offset)
    if pnum>1:
        pages_nums = range(pnum)
    else:
        pages_nums = None

    c = {
                 'logouturl':LOGOUT,
                 'is_admin':users.is_current_user_admin(),
                 'tips':reversed(mess),
                 'count':all_num,
                 'pages_nums':pages_nums,
                 'pageid':int(pageid),
                 'cur_user':CURUSER,
                 'offset':all_num-offset-limit, # the number of 1st
                 }
    return render_to_response( 'tips.htm',c)


def del_tip( request ):
    if not users.is_current_user_admin():
        return HttpResponseRedirect('/')
    mkey = Key(request.POST['mkey'])
    mes = Tip.get(mkey)
    mes.delete()
    return HttpResponse( 'deleted' )
