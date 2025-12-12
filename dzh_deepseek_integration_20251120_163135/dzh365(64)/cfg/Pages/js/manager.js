$(document).ready(function(){
	var uid = window.external.getDZHProperty("userid");
	var url = "/fateCodeProcess/user/customerManager?userName="+uid;
	Socket.send(url,setUser);
});

function setUser(managerData){
	document.getElementById("umanagerName").innerHTML = managerData[0].managerName;
	document.getElementById("umanagerPhone").innerHTML = managerData[0].managerPhone;
	document.getElementById("umanagerMail").innerHTML = managerData[0].managerMail;
	document.getElementById("umanagerTelphone").innerHTML = managerData[0].managerTelphone;
}
