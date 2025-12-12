/*
 Name:yangsen
*/
$(function(){
	var len = $(".img_list li").length;
	var img_w=$(".main").width();
	var img_h=img_h/1.8;
	$(".main").height(img_h);
	$(".img_list li").width(img_w);
	$(".img_list").width(len*img_w);
	var index = 0;
	//是鼠标滑过效果
	var s=0;
	$(".page_btn li").mouseover(function(){
		$(".img_list").stop();
		var i=$(this).index();
		var t=i*-img_w;
		$(".page_btn li").removeClass("onthis");
		$(this).addClass("onthis");
		$(".img_list").animate({left:t+'px'},500);
		index=i;
	});

	// Prev
	$(".step_last").click(function() {
		index -= 1;
		if(index == -1) {index = len - 1;}
		show_img(index*-img_w);
		show_step(index);
	});
	//next
	$(".step_next").click(function() {
		index += 1;
		if(index == len) {index = 0;}
		show_img(index*-img_w);
		show_step(index);
	});

	// mouse 
	$(".main").hover(function() {
		clearInterval(picTimer);
	},function() {
		picTimer = setInterval(function() {
			index++;
			if(index == len) {index = 0;}
			show_img(index*-img_w);
			show_step(index);
		//alert(img_w)
		},8000); 
	}).trigger("mouseleave");

	function show_img(l){
		$(".img_list").animate({left:l+'px'},500);
	}
	function show_step(s){
		$(".page_btn li").removeClass("onthis");
		$(".page_btn li").eq(s).addClass("onthis");
	}
});

window.onresize =function(){
	len = $(".img_list li").length;
	img_w=$(".main").width();
	img_h=img_h/1.8;
	$(".main").height(img_h);
	$(".img_list li").width(img_w);
	$(".img_list").width(len*img_w);
}
