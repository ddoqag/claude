$(function(){
	window.external.getSitemap().done(function(data){
		/// 添加节点 ///
		var nav_html = '', con_html = '';
		for (var i=0; i<data.length; i++) {
			nav_html += '<li rel="'+data[i].id+'"><a href="javascript:;">'+data[i].name+'</a></li>';
			con_html += '<section class="con_area" rel="'+data[i].id+'"><div class="content_zone"><div class="con_font">'+data[i].name+'</div><div class="stretch_btn"><div style="margin-top:-2px">ˇ</div></div></div>';
			for (var ci=0; ci<data[i].children.length; ci++) {
				con_html += '<div class="conz_font">' + data[i].children[ci].name + '</div><div class="con_list"><ul>';
				var theGrandchildren = data[i].children[ci].children;
				for (var gci=0; gci<theGrandchildren.length; gci++) {
					if (theGrandchildren[gci].children) {
						con_html += '<div class="con_list"><ul><li class="first"><a href="javascript:;">| '+theGrandchildren[gci].name+'</a></li>';
						for (var v=0; v<theGrandchildren[gci].children.length; v++) {
							con_html += '<li><a href="'+theGrandchildren[gci].children[v].link+'" onclick="window.external.closeDialog();">'+theGrandchildren[gci].children[v].name+'</a></li>';
						}
						con_html += '</ul></div>';
					} else {
						con_html += '<li><ul><a href="'+theGrandchildren[gci].link+'" onclick="window.external.closeDialog();">'+theGrandchildren[gci].name+'</a></ul></li>';
					}
				}
				con_html += '</ul></div>';
			}
			con_html += '</section>';
		}
		$("#nav").append('<ul>'+nav_html+'</ul>');
		$("#map").append(con_html);

		/// 第一个高亮 ///
		$('#nav ul li:eq(0)').addClass('selected_icon');

		/// 导航点击 ///
		$('#nav ul li').click(function(){
			$(this).addClass('selected_icon').siblings().removeClass('selected_icon');
			var last = $('.con_area:last');
			$('.con_area[rel='+$(this).attr('rel')+']').prevAll().slideUp('fast', function(){
				$(this).insertAfter(last).show();
			});
		});
    });
});
