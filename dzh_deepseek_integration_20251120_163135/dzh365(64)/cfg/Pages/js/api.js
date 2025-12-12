(function(){
	var env = 2; // 环境配置(外网:0, beta:1, alpha:2, dev:3)
	if (window.external) {
		window.external.env = env;
		window.external.getSessionUrl = 'http://f9data'+['','beta','alpha','dev'][env]+'.gw.com.cn/_api/cookie.php?action=get_session&callback=?';
		window.external.hostHelp = 'http://help'+['','beta','alpha','dev'][env]+'.gw.com.cn';
	}
}());
