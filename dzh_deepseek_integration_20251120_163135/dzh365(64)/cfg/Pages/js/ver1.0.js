$(function(){
	if (location.hash === '#parse') {
		var tree = {
			id:(location.pathname.match(/(\w+)\.html$/) || [, ''])[1],
			init:function () {
				$('.vbox').each(function (index, item) {
					$(item).find('>p').each(function (index, item) {
						tree.l1(tree, $(item), index);
					});
				});
				return {
					name:document.title.replace(/.*-/, ''),
					id:this.id,
					children:this.children
				};
			},
			l1:function (parent, child, index) {
				var node = {
					name:$.trim(child.text())
				};
				(child.next('ul').length ? child.next('ul').find('>li') : child.next('div').find('>ul>li')).each(function (index, item) {
					tree.l2(node, $(item), index);
				});
				if (node.name) {
					parent.children = parent.children || [];
					parent.children.push(node);
				}
			},
			l2:function (parent, child, index) {
				var node = {
						name:$.trim(child.text().replace(/\s+\n(?:.|\n)*/, ''))
					},
					link = child.find('>a:eq(0)');
				if (link.length) {
					node.link = link.attr('href');
				}
				if (child.parent('.tab_panel_title').length) {
					child.parent().next('div').find('ul:eq(' + index + ') li').each(function (index, item) {
						tree.l3(node, $(item), index);
					});
				} else if (child.hasClass('tooltipShow')) {
					child.find('>.tooltip a').each(function (index, item) {
						tree.l3(node, $(item), index);
					});
				}
				if (node.name) {
					parent.children = parent.children || [];
					parent.children.push(node);
				}
			},
			l3:function (parent, child, index) {
				var node = {
						name:$.trim(child.text())
					},
					link = child.attr('href') ? child : child.find('>a:eq(0)');
				if (link.length) {
					node.link = link.attr('href');
				}
				if (node.name) {
					parent.children = parent.children || [];
					parent.children.push(node);
				}
			}
		};
		return sessionStorage.setItem(tree.id, JSON.stringify(tree.init()));
	}

	window.external && external.closeDialog && $('body,.list_tip').on('click', 'a', function(e){
		external.closeDialog();
	});
	window.addEventListener('blur', function() {
		window.external && external.closeDialog && external.closeDialog();
	});
	$('#tab_panel_zt ul.tab_panel_title li').click(function(){
		$(this).addClass('hit2').siblings().removeClass('hit2');
		$('#panes>div:eq('+$(this).index()+')').show().siblings().hide();
	})

	$('#tab_panel_zj ul.tab_panel_title li').click(function(){
		$(this).addClass('hit2').siblings().removeClass('hit2');
		$('#panes_zj>div:eq('+$(this).index()+')').show().siblings().hide();
	})

	$('#tab_panel_gmt ul.tab_panel_title li').click(function(){
		$(this).addClass('hit2').siblings().removeClass('hit2');
		$('#panes_gmt>div:eq('+$(this).index()+')').show().siblings().hide();
	})

	$('#tab_panel_otc ul.tab_panel_title li').click(function(){
		$(this).addClass('hit2').siblings().removeClass('hit2');
		$('#panes_otc>div:eq('+$(this).index()+')').show().siblings().hide();
	})

	$('#tab_panel_zs ul.tab_panel_title li').click(function(){
		$(this).addClass('hit2').siblings().removeClass('hit2');
		$('#panes_zs>div:eq('+$(this).index()+')').show().siblings().hide();
	})

	$('#tip_ul>li>div.hg_dropup').click(function(){
		$(this).parent().children('.tooltip').toggle();
		$(this).parent().siblings().children('.tooltip').hide();
	});

	$('#tip_ul2>li>div.hg_dropup').click(function(){
		$(this).parent().children('.tooltip_n').toggle();
		$(this).parent().siblings().children('.tooltip_n').hide();
	});

	$(document).click(function(){
		$(".tooltip").hide();
	});

	$('#tip_ul>li>div.hg_dropup').click(function (e) {
		e.stopPropagation();//阻止事件向上冒泡
	});

	$('#tip_ul>li>.tooltip').click(function (e) {
		e.stopPropagation();//阻止事件向上冒泡
	});

	$(".list_tip a").hover(function(){
		$(this).addClass("select").siblings().removeClass("select");
	});

	$('.tips_ul5>li>div.hg_dropup').click(function(){
		$('.tips_ul8>li>div.tooltip').hide();
		$(this).parent().children('.tooltip').toggle();
		$(this).parent().siblings().children('.tooltip').hide();
	});

	$('.tips_ul8>li>div.hg_dropup').click(function(){
		$('.tips_ul5>li>div.tooltip').hide();
		$(this).parent().children('.tooltip').toggle();
	});

	$('.tips_ul>li>div.hg_dropup').click(function (e) {
		e.stopPropagation();//阻止事件向上冒泡
	});

	$('.tips_ul>li>.tooltip').click(function (e) {
		e.stopPropagation();//阻止事件向上冒泡
	});
});
