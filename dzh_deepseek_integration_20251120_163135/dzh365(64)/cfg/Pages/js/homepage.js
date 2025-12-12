var n = 0, count;
$(document).ready(function(){
	count = $("#banner_data a").length;

	/// 轮播切换 ///
	$("#banner_btn li").click(function(){
		var i = $(this).index();
		n = i;
		if (i >= count) return;
		$('#banner_content div').hide();
		$(this).css("background","#ee7b0b").siblings().css("background","#656565");
		var url = $("#banner_data a img").eq(i).attr('src');
		$('#banner_swap').stop().css('opacity', '0').css('background-image', 'url('+url+')').animate({opacity:'1'}, {duration:1000, complete:function(){
			$('#banner_content div').eq(i).show();
			$('#banner').css('background-image', 'url('+url+')');
		}});
	});
	$("#banner_btn li").eq(0).trigger('click');

	/// 定时触发 ///
	t = setInterval("showAuto()", 8000);
	$("#banner").hover(function(){
		clearInterval(t)
	}, function(){
		t = setInterval("showAuto()", 8000);
	});

	/// 链接改造 ///
	$.getJSON(external.getSessionUrl, function(data){
		if (data) {
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
	n = n >= (count - 1) ? 0 : ++n;
	$("#banner_btn li").eq(n).trigger('click');
}






