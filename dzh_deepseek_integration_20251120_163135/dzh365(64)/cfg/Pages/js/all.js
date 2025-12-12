/*–- 禁止选择文本： -–*/
var omitformtags=["input", "textarea", "select"]
omitformtags=omitformtags.join("|")
function disableselect(e){
if (omitformtags.indexOf(e.target.tagName.toLowerCase())==-1)
return false
}
function reEnable(){
return true
}
if (typeof document.onselectstart!="undefined")
document.onselectstart=new Function ("return false")
else{
document.onmousedown=disableselect
document.onmouseup=reEnable
};
//鼠标点击加载二级菜单
function showMune2_(m){
	var mune2_m =$(".Mune2_"+m);
	var menu_ico1_m=$(".menu_ico1_"+m);
	mune2_m.siblings().hide();
	mune2_m.show();
	menu_ico1_m.addClass("menu_ico_click");
	menu_ico1_m.siblings().removeClass("menu_ico_click");
	var munebgh=mune2_m.height()+20;
	var munebgw=mune2_m.width()+20;
	$(".Mune_bg").css({ width: munebgw, height: munebgh });
	$(".Mune_bg2").show();
	$(".Mune3").hide();
	$(".Mune_bg").hide();
	$(".menu_z").removeClass("menu3_ico_click");
	$(".menu_ico").removeClass("menu_ico_click2");
};
//加载一级菜单并且默认显示第几个
function test() {
           window.open(url,'height=100,width=400,top=0,left=0,toolbar=no,menubar=no,scrollbars=no,resizable=no,location=no,status=no');
      }
//鼠标点击二级加载三级菜单
function showMune3_(m){
	$(".Mune4").hide();
	var mune3_m=$(".Mune3_"+m);
	var mune_ico3_m=$(".menu_ico3_"+m);
	mune3_m.siblings().hide();
	mune3_m.show();
	var munebgh=mune3_m.height();
	var munebgw=mune3_m.width()+10;
	$(".Mune_bg4").css({ width: munebgw, height: munebgh });
	$(".Mune_bg").show();
	mune_ico3_m.addClass("menu3_ico_click");
	mune_ico3_m.siblings().removeClass("menu3_ico_click");
	$(".menu_ico_click").addClass("menu_ico_click2");
};
//鼠标点击二级加载四级菜单
function showMune4_(m){
	var mune4_m=$(".Mune4_"+m);
	var mune_ico4_m=$(".menu_ico4_"+m);
	mune4_m.siblings().hide();
	mune4_m.show();
	$(".Mune_bg4").show();
	mune_ico4_m.addClass("menu3_ico_click");
	mune_ico4_m.siblings().removeClass("menu3_ico_click");
	$(".menu_ico_click").addClass("menu_ico_click2");
};
//鼠标划出二级隐藏三级菜单
function hideMune3(){
	$(".Mune3").hide();
	$(".Mune_bg").hide();
	$(".menu_z").removeClass("menu3_ico_click");
	$(".menu_ico").removeClass("menu_ico_click2");
};
function hideMune4(){
	$(".Mune4").hide();
	$(".Mune_bg4").hide();
	$(".menu_z4").removeClass("menu3_ico_click");
	$(".menu_ico").removeClass("menu_ico_click2");
};
function hideMune2(){
	$(".mune2").hide();
	$(".Mune_bg2").hide();
	$(".menu_ico").removeClass("menu_ico_click");
};
function closeMune(){
	$(".menu_box_bg").fadeOut();
	$(".menu_box").fadeOut();
	};
$(function(){
	$(".Mune_bg").click(function(){
		$(".Mune3").hide();
		$(".Mune_bg").hide();
		$(".Mune_bg4").hide();
		$(".menu_z").removeClass("menu3_ico_click");
		$(".menu_z4").removeClass("menu3_ico_click");
		$(".menu_ico").removeClass("menu_ico_click2");
		$(".Mune4").hide();	});
	$(".menu_ico").click(function(){
		$(".Mune3").hide();
		$(".Mune_bg").hide();
		$(".menu_z").removeClass("menu3_ico_click");
		$(".menu_ico").removeClass("menu_ico_click2");	});
	$(".Mune_bg2").click(function(){
		$(".mune2").hide();
		$(".Mune_bg2").hide();
		$(".menu_ico").removeClass("menu_ico_click");});
	$(".Mune_bg4").click(function(){
		$(".Mune4").hide();
		$(".Mune_bg4").hide();
		$(".menu_z4").removeClass("menu3_ico_click");
		$(".menu_ico").removeClass("menu_ico_click2");	});
	$(".menu_z").click(function(){
		$(".Mune_bg4").hide();
		$(".Mune4").hide();
		$(".menu_z4").removeClass("menu3_ico_click");
		$(".menu_ico").removeClass("menu_ico_click2");	});
});
window.onerror = function(){  
        return true;  
    }