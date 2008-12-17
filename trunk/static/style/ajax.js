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
    var se_id=transport.responseText;
    
    var tr = new Element('tr',{'id':'tr_'+se_id});
    var td_isdone = new Element('td',{'class':'checkbox'});
    var td_content = new Element('td',{'id':se_id+'_cont',
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
            'value':se_id,
            'id':'id_'+se_id
        });
    checkbox = new Element( 'input',{'type':'checkbox',
                                     'id':'checkbox_'+se_id,
                                     'onclick':'done_se('+se_id+')'} );
    td_isdone.insert( hidden );
    td_isdone.insert( checkbox );

    a_edit = new Element( 'a',{'href':'#','onclick':'edit_se('+se_id+')'});
    td_edit.insert( a_edit );
    img_edit =new Element( 'img',{'src':'/static/images/edit.jpg'});
    a_edit.insert( img_edit );
    
    a_del = new Element( 'a',{'href':'#','onclick':'del_se('+se_id+')'});
    td_del.insert( a_del );
    img_del =new Element( 'img',{'src':'/static/images/del.jpg'});
    a_del.insert( img_del );

    //reset form add_sub_event
    $('id_content').value ='';
    $('id_start_date').value ='';
    $('id_end_date').value ='';
}

function edit_se_to_html( transport )
{
		var id=transport.responseText;
		$(id+"_cont").innerHTML =  $F('id_content');
		$(id+"_sdate").innerHTML =  $F('id_start_date');
		$(id+"_edate").innerHTML =  $F('id_end_date');	
		
		close_addse();
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
        $('tr_'+id).style.color = "grey";
    }
    else{
        $('tr_'+id).style.color = "black";
    }
}

function add_sub_event()
{   
      var myAjax = new Ajax.Request('../add_sub_event/',{
            method:'POST',
			parameters:{event_id:$F('event_id'),
                        content:$F('id_content'),
                        start_date:$F('id_start_date'),
                        end_date:$F('id_end_date')
            },
            onSuccess:add_se_to_html,
            onFailure:function( transport ){alert( transport.status );
            }
            })
}
function edit_sub_event( se_id )
{  
      var myAjax = new Ajax.Request('../edit_sub_event/',{
            method:'POST',
			parameters:{id:se_id,
                        content:$F('id_content'),
                        start_date:$F('id_start_date'),
                        end_date:$F('id_end_date')
            },
            onSuccess:edit_se_to_html,
            onFailure:function( transport ){alert( transport.status );
            }
            })    
}
function del_se( se_id )
{  
      var myAjax = new Ajax.Request('../del_sub_event/',{
            method:'POST',
			parameters:{id:se_id},
            onSuccess:del_se_to_html,
            onFailure:function( transport ){alert( transport.status );
            }
            })    
}
function done_se( se_id )
{
    var isdo = $('checkbox_'+se_id).checked;
    var myAjax = new Ajax.Request('../done_sub_event/',{
            method:'POST',
			parameters:{id:se_id,isdone:isdo},
            onSuccess:done_se_to_html,
            onFailure:function( transport ){alert( transport.status );
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

function edit_se( id )
{
    $('id_content').value = $(id+'_cont').innerHTML.strip();
    $('id_start_date').value = $(id+'_sdate').innerHTML.strip();
    $('id_end_date').value = $(id+'_edate').innerHTML.strip();
    $('but_submit_se').value = "提交修改";
    $('but_submit_se').onclick = new Function("edit_sub_event("+id+")");

    flag = true;
    $('submit_subevent').show();
    $('switch_addse').hide();
}
//send request for asking add friends
function show_box( to_id )
{
	$('mes_box').show();
	$('to_user').value = to_id;
	$('message').value = '';
}

function send_request()
{
	var op='op_'+$F('to_user');
    var myAjax = new Ajax.Request('../addfriend/',{
            method:'POST',
			parameters:{uid:$F('to_user'),message:$F('message')},
            onSuccess:function( transport ){$(op).innerHTML='已发送好友请求';$('mes_box').hide();},
            onFailure:function( transport ){alert( transport.status );
            }
        })    
}

function accept_friend( uid )
{
	var uname=$('uname_'+uid).value;
	var myAjax = new Ajax.Request('../acceptfriend/',{
		method:'POST',
		parameters:{uid:uid},
		onSuccess:function(){$('request_'+uid).update('您已和'+uname+'成为好友。');},
		onFailure:function( transport ){alert( transport.status );
		}
	})   
}

function deny_friend( uid )
{
	var uname=$('uname_'+uid).value;	
	var myAjax = new Ajax.Request('../deny/',{
		method:'POST',
		parameters:{uid:uid},
		onSuccess:function(){$('request_'+uid).update('您已拒绝'+uname+'的好友请求。')},
		onFailure:function( transport ){alert( transport.status );
		}
	})   
}

function remove_friend( uid )
{
	var myAjax = new Ajax.Request('../removefriend/',{
		method:'POST',
		parameters:{uid:uid},
		onSuccess:function(){$('fr_'+uid).remove()},
		onFailure:function( transport ){alert( transport.status );
		}
	})   
}

function add_to_concern( eid )
{
	$('mes_box').show();
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
		onFailure:function( transport ){alert( transport.status );
		}
	})   
}

function remove_concern( eid,ce_id )
{
	var myAjax = new Ajax.Request('../remove_concern/',{
		method:'POST',
		parameters:{eid:eid,ce_id:ce_id},
		onSuccess:function(){$('ce_'+ce_id).remove();},
		onFailure:function( transport ){alert( transport.status );
            }
        })   
}

function del_event()
{
	$('del_confirm_box').show();
}

function send_del( eid )
{
	var myAjax = new Ajax.Request('../del_event/',{
		method:'POST',
		parameters:{eid:eid},
        onSuccess:function( transport ){window.location.replace('../home');
            },
        onFailure:function( transport ){alert( transport.status );
            }
                                        
        })   
}
function add_comment_to_html( transport )
{
	var time=transport.responseText;
	comment_body=$('comment_body');
	var div = new Element('div',{'class':'each_com'});
	comment_body.insert(div);
	var div_top = new Element('div',{'class':'com_info'});
	div.insert(div_top);
	var a=new Element('a',{'href':'../home/?user='+$F('visitor_id') }).update( $F('visitor_name') );
	div_top.insert(a);
	var span=new Element('span',{'class':'time'}).update(time);
	div_top.insert(span);
	var p=new Element('p').update($F('write_comment'));
	div.insert(p);
	$('write_comment').value='';
}
	  
function submit_comment(bid)
{   
      var myAjax = new Ajax.Request('../add_comment/',{
            method:'POST',
			parameters:{bid:bid,
                        content:$F('write_comment')},
            onSuccess:add_comment_to_html,
            onFailure:function( transport ){alert( transport.status );
            }
            })
}
function del_comment( cid )
{
    var myAjax = new Ajax.Request('../del_comment/',{
            method:'POST',
			parameters:{cid:cid},
            onSuccess:function(){$('com_'+cid).remove();},
            onFailure:function( transport ){alert( transport.status );
            }
        })
}

function add_mes_to_html( transport )
{
	var time=transport.responseText;
	mes_body=$('mes_body');
	var div = new Element('div',{'class':'each_comment'});
	mes_body.insert(div);
	var div_top = new Element('div',{'class':'mes_info'});
	div.insert(div_top);
	var a=new Element('a',{'href':'../home/?user='+$F('visitor_id') }).update( $F('visitor_name') );
	div_top.insert(a);
	var span=new Element('span',{'class':'time'}).update(time);
	div_top.insert(span);
	var p=new Element('p').update($F('write_mes'));
	div.insert(p);
	$('write_mes').value='';
}

function submit_mes()
{   
      var myAjax = new Ajax.Request('../add_mes/',{
            method:'POST',
			parameters:{content:$F('write_mes'),},
            onSuccess:add_mes_to_html,
            onFailure:function( transport ){alert( transport.status );
            }
            })
}
function del_mes( mid )
{
    var myAjax = new Ajax.Request('../del_mes/',{
            method:'POST',
			parameters:{mid:mid},
            onSuccess:function(){$('mes_'+mid).remove();},
            onFailure:function( transport ){alert( transport.status );
            }
        })
}


function addblog()
{
	var oform=document.getElementById("editblog")
	if(oform.title.value=="")
	{
		alert("Empty title!");
		return;
	}
	if(oform.content.value=="")
	{
		alert("Empty content!");
		return;
	}
	if(oform.post_type.value=="")
	{
		oform.post_type.value="new";
	}
	if(oform.post_type.value=="old")
	{
		oform.action="../display_blog/";
	}
	oform.submit();
	oform.action=".";
}
function display_blog()
{
	var oform=document.getElementById("blog_info")
	if(oform.blog_info.value=="")
	{
		alert("No blog id!");
		return false;
	}
	if(oform.event_info.value=="")
	{

	}
	oform.action="../display/";
	oform.submit();
}
function edit_blog()
{
	var oform=document.getElementById("blog_info")
	if(oform.blog_info.value=="")
	{
		alert("No blog id!");
		return false;
	}
	if(oform.event_info.value=="")
	{

	}
	oform.action="../edit_blog/";
	oform.submit();
}
function del_blog()
{
	var oform=document.getElementById("blog_info")
	if(oform.blog_info.value=="")
	{
		alert("No blog id!");
		return false;
	}
	if(oform.event_info.value=="")
	{

	}
	oform.action="../del_blog/";
	oform.submit();
}
function addcomment()
{
	var oform=document.getElementById("my_newcomment")
	if(oform.new_content.value=="")
	{
		alert("Empty content!");
		return false;
	}
	if(oform.blog_id.value=="")
	{
		alert("No blog id!");
		return false;
	}
	if(oform.event_id.value=="")
	{

	}
	oform.submit();
}

function delete_comment(com_id)
{
	
	var oform=document.getElementById("comment_info")
	if(oform.blog_id_info.value=="")
	{
		alert("No blog id!");
		return false;
	}
	if(oform.event_id_info.value=="")
	{

	}
	oform.comment_id_info.value=com_id;
	oform.submit();
}