var cur="new_event";
function sw(str){
	$(cur,str).invoke('toggle');
	cur_title=cur+"_title";
	$(cur_title).setStyle({borderBottomColor:'#D9001D'});
	str_title=str+"_title";
	$(str_title).setStyle({borderBottomColor:'#FFF'});
	cur=str;
}
var cur2="event_plan";
function sw2(str){
	$(cur2,str).invoke('toggle');
	cur_title=cur2+"_title";
	$(cur_title).setStyle({borderBottomColor:'#D9001D'});
	str_title=str+"_title";
	$(str_title).setStyle({borderBottomColor:'#FFF'});
	cur2=str;
}

function switch_comment(){
	$('tbody_com').toggle();
	$('comment_counter').toggleClassName('dot_triright');
}