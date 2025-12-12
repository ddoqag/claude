$(document).ready(function(){
	$.getJSON(external.getSessionUrl, function(data){
		var md = JSON.parse(data.qxd)["112"];
		var tt = new Date(parseInt(md) * 1000);
		var endT = tt.getFullYear()+'年'+(tt.getMonth()+1)+'月'+tt.getDate()+'日';
		document.getElementById("dateend").innerHTML = endT;
	});
	var uid = window.external.getDZHProperty("userid");
	var url = "/fateCodeProcess/user/customerManager?userName="+uid;
	Socket.send(url,setUser);
});

function setUser(managerData){
	var uid = window.external.getDZHProperty("userid");
	document.getElementById("uid").innerHTML = uid;
	document.getElementById("umanagerName").innerHTML = managerData[0].managerName;
	document.getElementById("umanagerPhone").innerHTML = managerData[0].managerPhone;
	document.getElementById("umanagerMail").innerHTML = managerData[0].managerMail;
	document.getElementById("umanagerTelphone").innerHTML = managerData[0].managerTelphone;
}
