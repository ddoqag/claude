$(function(){
	var len=$(".tower li").length;
	var a=0;
	
	$(".star").hover(function(){
		$(".loac").show();
	},function(){});	
	$(".countrcy").hover(function(){
		},function(){
		$(".loac").hide();
	});
	$(".tower li").not(":first").hide();
		
		time01=setInterval(function(){
			a++;
			if(a==len){a=0};
			$(".tower li").eq(a).fadeIn().siblings().hide();
			
		},5000);
		$(".bto_ctrl").click(function(){
			$(this).toggleClass("stop");
		});
		$(".bto_ctrl").hover(function(){
			$(".bto_ctrl").removeClass("bto_ctrl2")
			},function(){
				if(!$(".bto_ctrl").hasClass("stop")){$(".bto_ctrl").addClass("bto_ctrl2")}
			
		})
		$(".bto_ctrl").toggle(function(){
			clearInterval(time01);
			},function(){
				time01=setInterval(function(){
					a++;
					if(a==len){a=0};
					$(".tower li").eq(a).fadeIn().siblings().hide();
				},5000);
			})
		
		
		
})

