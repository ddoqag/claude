var t = n = 0, count;
$(document).ready(function(){
	count = $("#banner_list a").length;
	$('#banner').css('background-image', 'url('+$("#banner_list a img").eq(0).attr('src')+')');
	$('#banner_click').attr('href', $("#banner_list a").eq(0).attr('href'));
	$("#banner li").click(function(){
		var i = $(this).index();
		n = i;
		if (i >= count) return;
		$('#banner').css('background-image', 'url('+$("#banner_list a img").eq(i).attr('src')+')');
		$('#banner_click').attr('href', $("#banner_list a").eq(i).attr('href'));
		$(this).css("background","#da6f13").siblings().css("background","#656565");
	});
	t = setInterval("showAuto()",8000);
	$("#banner").hover(function(){
		clearInterval(t)
	}, function(){
		t = setInterval("showAuto()",8000);
	});

	$.getJSON(external.getSessionUrl, function(data){
		if(data){
			$('a.user_link').each(function(){
				$(this).attr('href', $(this).attr('rel'));
			});
		}
		else{ console.log('not login'); }
	});
	$('a.help_link').each(function(){
		var href = $(this).attr('href').replace('http://help.gw.com.cn', external.hostHelp);
		$(this).attr('href', href);
	});
});
function showAuto(){
	n = n >=(count-1) ? 0 : ++n;
	$("#banner li").eq(n).trigger('click');
}






