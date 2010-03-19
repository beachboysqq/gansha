function get_img(){
	var path=$F('headshot');	
	var ext=(path.substring(path.lastIndexOf(".")+1)).toLowerCase();

	if( path ){
		if( ext=='jpg' || ext=='gif' || ext=='png'){
			//only IE support preview the image.
			if( navigator.userAgent.indexOf('MSIE')>=0 ){
				img="<img src='"+path+"'/>";
				$('myinfo_error').update(img);
			}
		}
		else{
			$('myinfo_error').update('Image should be jpg,gif or png file.');
		}
	}
}

function add_se_to_html( transport )
{
    var sekey=transport.responseText;
    
    var tr = new Element('tr',{'id':'tr_'+sekey});
    var td_isdone = new Element('td',{'class':'checkbox'});
    var td_content = new Element('td',{'id':sekey+'_cont',
            'class':'underline_grey'}).update( $F('id_content') );

    var sdate = $F('id_start_date');
    var edate = $F('id_end_date');
    var td_sdate = new Element('td',{'class':'underline_grey font_10'}).update( sdate );
    var td_edate = new Element('td',{'class':'underline_grey font_10'}).update( edate );
    var td_edit = new Element('td',{'class':'underline_grey text_center'});
    var td_del = new Element('td',{'class':'underline_grey text_center'});
    
    var tbody = $('tbody_se');
    tbody.insert( tr );
    tr.insert( td_isdone );
    tr.insert( td_content );
    tr.insert( td_sdate );
    tr.insert( td_edate );
    tr.insert( td_edit );
    tr.insert( td_del );
   
    hidden = new Element( 'input',{
            'type':'hidden',
            'value':sekey,
            'id':'id_'+sekey
        });
    checkbox = new Element( 'input',{'type':'checkbox',
                                     'id':'checkbox_'+sekey,
                                     'onclick':'done_se(\''+sekey+'\')'} );
    td_isdone.insert( hidden );
    td_isdone.insert( checkbox );

    a_edit = new Element( 'a',{'href':'#','onclick':'edit_se('+sekey+')'});
    td_edit.insert( a_edit );
    img_edit =new Element( 'img',{'src':'/static/images/edit.jpg'});
    a_edit.insert( img_edit );
    
    a_del = new Element( 'a',{'href':'#','onclick':'del_se('+sekey+')'});
    td_del.insert( a_del );
    img_del =new Element( 'img',{'src':'/static/images/del.jpg'});
    a_del.insert( img_del );

    //reset form add_sub_event
    $('id_content').value ='';
    $('id_start_date').value ='';
    $('id_end_date').value ='';
}

function del_se_to_html( transport )
{
	var id=transport.responseText;
	$('tr_'+id).remove();
}

function done_se_to_html( transport )
{
    var id=transport.responseText;
    if( $('checkbox_'+id).checked ){
        $('tr_'+id).style.color = "#999";
        // $('tr_'+id).style.cssText = "color:grey;";
    }
    else{
        $('tr_'+id).style.color = "#000";
        // $('tr_'+id).style.cssText = "color:black;";
    }
}

function add_sub_event()
{   
      var myAjax = new Ajax.Request('../add_sub_event/',{
            method:'POST',
			parameters:{content:$F('id_content'),
                        start_date:$F('id_start_date'),
                        end_date:$F('id_end_date')
            },
            onSuccess:add_se_to_html,
            onFailure:function( transport ){alert( transport.status );
            }
            })
}

function add_tip(){
	$('tip_content').innerHTML = '<textarea id="tip_content_input" class="textarea"></textarea><input type="button" value="保存" onclick="submit_tip()"/>';
}

function submit_tip()
{   
      var myAjax = new Ajax.Request('../addtip/',{
          method:'POST',
		  parameters:{content:$F('tip_content_input')}
		  ,
		  onSuccess:add_tip_to_html,
		  onFailure:function( transport ){alert( transport.status );}
	  })
}

function add_tip_to_html( transport ){
	$('tip_content').innerHTML = transport.responseText;
}

function del_tip( mkey )
{
    var myAjax = new Ajax.Request('../deltip/',{
            method:'POST',
			parameters:{mkey:mkey},
            onSuccess:function(){
				$('tr1_tip_'+mkey,'tr2_tip_'+mkey).invoke('remove');
			},
            onFailure:function( transport ){alert( transport.status )
            }
        })
}

function edit_se_to_html( transport )
{
		var isexpired=transport.responseText;
		var id = $F('cur_edit_se');
		$(id+"_cont").innerHTML =  $F('id_content');
		$(id+"_sdate").innerHTML =  $F('id_start_date');
		$(id+"_edate").innerHTML =  $F('id_end_date');	
		if( isexpired=='True' ){
			$('tr_'+id).style.color = "#F00";
		}
		else{
			$('tr_'+id).style.color = "#000";
		}
		close_addse();
}

function edit_sub_event( sekey )
{  
	$('cur_edit_se').value = sekey;
	var myAjax = new Ajax.Request('../edit_sub_event/',{
            method:'POST',
			parameters:{key:sekey,
                        content:$F('id_content'),
                        start_date:$F('id_start_date'),
                        end_date:$F('id_end_date')
            },
            onSuccess:edit_se_to_html,
            onFailure:function( transport ){alert( transport.status );
            }
            })    
}

function del_se( sekey )
{  
      var myAjax = new Ajax.Request('../del_sub_event/',{
            method:'POST',
			parameters:{key:sekey},
            onSuccess:del_se_to_html,
            onFailure:function( transport ){alert( transport.status )
            }
            })    
}

function done_se( sekey )
{
    var isdo = $('checkbox_'+sekey).checked;
    var myAjax = new Ajax.Request('../done_sub_event/',{
            method:'POST',
			parameters:{key:sekey,is_done:isdo},
            onSuccess:done_se_to_html,
            onFailure:function( transport ){alert( transport.status )
            }
        })    
}
//flag=true,indentify the sub event adding form displayed,
//otherwise,it's hidden.
var flag = false;

function switch_addse()
{
    //reset form add_sub_event
    $('id_content').value = '';
    $('id_start_date').value = '';
    $('id_end_date').value = '';
    $('but_submit_se').value = "添 加";
    $('but_submit_se').onclick = add_sub_event;
    
    if( !flag ){
        $('submit_subevent').show();
        $('switch_addse').hide();
        flag = true;
    }
}

function close_addse()
{
    flag = false;
    $('submit_subevent').hide();
    $('switch_addse').show();
}

//create eidt face
function edit_se( sekey )
{
    $('id_content').value = $(sekey+'_cont').innerHTML.strip();
    $('id_start_date').value = $(sekey+'_sdate').innerHTML.strip();
    $('id_end_date').value = $(sekey+'_edate').innerHTML.strip();
    $('but_submit_se').value = "提交修改";
    $('but_submit_se').onclick = new Function("edit_sub_event('"+sekey+"')");

    flag = true;
    $('submit_subevent').show();
    $('switch_addse').hide();
}

//send request for asking add friends
function show_box( uemail )
{
	$('mes_box').show();
	$('mes_box').scrollTo();
	$('to_user').value = uemail;
	$('message').value = '';
}

function send_request()
{
	var op='op_'+$F('to_user');
    var myAjax = new Ajax.Request('../addfriend/',{
            method:'POST',
			parameters:{uemail:$F('to_user'),message:$F('message')},
            onSuccess:function( transport ){$(op).innerHTML='已发送';$('mes_box').hide();},
            onFailure:function( transport ){alert( transport.status )
            }
        })    
}

function accept_friend( uemail )
{
	var uname=$('uname_'+uemail).value;
	var myAjax = new Ajax.Request('../acceptfriend/',{
		method:'POST',
		parameters:{uemail:uemail},
		onSuccess:function(){$('request_'+uemail).update('您已和'+uname+'成为好友。');},
		onFailure:function( transport ){alert( transport.status )
		}
	})   
}

function deny_friend( uemail )
{
	var uname=$('uname_'+uemail).value;	
	var myAjax = new Ajax.Request('../deny/',{
		method:'POST',
		parameters:{uemail:uemail},
		onSuccess:function(){$('request_'+uemail).update('您已拒绝'+uname+'的好友请求。')},
		onFailure:function( transport ){alert( transport.status )
		}
	})   
}

function remove_friend( uemail )
{
	var myAjax = new Ajax.Request('../removefriend/',{
		method:'POST',
		parameters:{uemail:uemail},
		onSuccess:function(){$('fr_'+uemail).remove()},
		onFailure:function( transport ){alert( transport.status )
		}
	})   
}

function add_to_concern( eid )
{
	$('mes_box').show();
    $('mes_box').scrollTo();
    $('recorder').value = eid;
}

function send_concern()
{
	var eid=$F('eid');
	var ce_id=$F('recorder');
	var myAjax = new Ajax.Request('../add_to_concern/',{
		method:'POST',
		parameters:{eid:eid,ce_id:ce_id},
		onSuccess:function(){$('span_'+ce_id).update('[已关注]');$('mes_box').hide();},
		onFailure:function( transport ){alert( transport.status )
		}
	})   
}

function remove_concern( eid,ce_id )
{
	var myAjax = new Ajax.Request('../remove_concern/',{
		method:'POST',
		parameters:{eid:eid,ce_id:ce_id},
		onSuccess:function(){$('ce_'+ce_id).remove();},
		onFailure:function( transport ){alert( transport.status )
            }
        })   
}

function del_event()
{
	$('del_confirm_box').show();
}

function send_del()
{
	var myAjax = new Ajax.Request('../del_event/',{
		method:'POST',
		parameters:{},
        onSuccess:function( transport ){window.location.replace('../home');
            },
        onFailure:function( transport ){alert( transport.status )
            }                               
        })   
}
function add_comment_to_html( transport )
{
	var time=transport.responseText;
	var num=Number($('num_comment').innerHTML) + 1;
	comment_body=$('tbody_com');
	var div = new Element('div',{'class':'each_com'});
	comment_body.insert(div);
	var div_top = new Element('div',{'class':'com_info'});
	div.insert(div_top);
	//var a=new Element('a',{'href':'../home/?user='+$F('visitor_key') });
    //a.update( $F('visitor_name') );
	div_top.insert("#"+num+" &nbsp;");
	div_top.insert($F('visitor_name'));
	var span=new Element('span',{'class':'time'}).update(time);
	div_top.insert(span);
	var p=new Element('p').update($F('write_comment'));
	div.insert(p);
	$('write_comment').value='';
	//update counter
	$('num_comment').update( num );
}
	  
function submit_comment(bkey)
{   
      var myAjax = new Ajax.Request('../add_comment/',{
            method:'POST',
			parameters:{bkey:bkey,
                        content:$F('write_comment')},
            onSuccess:add_comment_to_html,
            onFailure:function( transport ){alert( transport.status )
            }
            })
}
function del_comment( ckey )
{
    var myAjax = new Ajax.Request('../del_comment/',{
            method:'POST',
			parameters:{ckey:ckey},
            onSuccess:function(){
				$('com_'+ckey).remove();
				$('num_comment').update( Number($('num_comment').innerHTML) - 1 );
			},
            onFailure:function( transport ){alert( transport.status )
            }
        })
}

function add_mes_to_html( transport )
{
    var time=transport.responseText;
	var tr1 = new Element('tr');
	var tr2 = new Element('tr');
	var td1 = new Element('td');

	var a=new Element('a',{'href':'../home/?user='+$F('visitor_id') }).update( $F('visitor_name') );
	var span=new Element('span',{'class':'time'}).update(time);
	var td2=new Element('td',{'class':'each_mes'}).update($F('write_mes'));
 
    mes_body=$('tbody_mes');
	mes_body.insert(tr1);

	mes_body.insert(tr2);
    tr1.insert(td1);
    tr2.insert(td2);    
	num=Number($('num_mes').innerHTML) + 1
	td1.insert("#"+num+" &nbsp;");
	td1.insert(a);
	td1.insert(span);
	$('write_mes').value='';
	//update count
	$('num_mes').update( num );
}

function submit_mes()
{   
      var myAjax = new Ajax.Request('../add_mes/',{
            method:'POST',
			parameters:{content:$F('write_mes')},
            onSuccess:add_mes_to_html,
            onFailure:function( transport ){alert( transport.status )
            }
            })
}
function del_mes( mkey )
{
    var myAjax = new Ajax.Request('../del_mes/',{
            method:'POST',
			parameters:{mkey:mkey},
            onSuccess:function(){
				$('tr1_mes_'+mkey,'tr2_mes_'+mkey).invoke('remove');
				$('num_mes').update( Number($('num_mes').innerHTML) - 1 );
			},
            onFailure:function( transport ){alert( transport.status )
            }
        })
}

function del_blog(bkey)
{
	$('del_blog_name').update( $('name_'+bkey ).innerHTML );
	$('del_blog_confirm_box').show();
	$('recorder_bkey').value = bkey;
}

function del_blog_real()
{
	bkey = $F('recorder_bkey');
	$('del_blog_confirm_box').hide();
    var myAjax = new Ajax.Request('../delblog/',{
            method:'POST',
			parameters:{blog:bkey},
            onSuccess:function(){
				$('tr_blog_'+bkey).remove();
			},
            onFailure:function( transport ){alert( transport.status )
            }
        })	
}
//在blogview中删除blog
function del_blog_real3()
{
	bkey = $F('recorder_bkey');
	$('del_blog_confirm_box').hide();
    var myAjax = new Ajax.Request('../delblog/',{
            method:'POST',
			parameters:{blog:bkey},
            onSuccess:function(){
				$('div_blog_'+bkey).remove();
			},
            onFailure:function( transport ){alert( transport.status )
            }
        })	
}

//在blog页面，删除blog
function del_blog_real2()
{
	bkey = $F('recorder_bkey');
	$('del_blog_confirm_box').hide();
    var myAjax = new Ajax.Request('../delblog/',{
        method:'GET',
		parameters:{blog:bkey},
        onSuccess:function(){
			window.location.replace('../event/');
		},
        onFailure:function( transport ){alert( transport.status )
									   }
        })	
}