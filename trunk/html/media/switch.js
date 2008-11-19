var cur="new_event";
function sw(str){
	$(cur,str).invoke('toggle');
	cur_title=cur+"_title";
	$(cur_title).setStyle({borderBottomColor:'#D9001D'});
	str_title=str+"_title";
	$(str_title).setStyle({borderBottomColor:'#FFF'});
	cur=str;
}
