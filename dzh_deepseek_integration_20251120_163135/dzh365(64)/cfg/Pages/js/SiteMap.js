(function ($) {
	if (window.external) {
		external.getSitemap = function () {
			var fn = arguments.callee,
				deferred = $.Deferred();
			if (fn.items) {
				return deferred.resolve(fn.items);
			} else {
				var list = [
					'stock',
					'bond',
					'commodity',
					'fund',
					'financial',
					'index',
					'forex',
					'macro',
					'industry',
					'news',
					'investment',
					'people',
					'vedio',
					'stkselanalysis'
				],
				loaded = 0,
				fragment = document.createElement('div');
				list.forEach(function (item) {
					var node = document.createElement('iframe');
					node.src = item + '.html#parse';
					node.addEventListener('load', function (e) {
						if (++loaded === list.length) {
							var items = [];
							list.forEach(function (item) {
								items.push(JSON.parse(sessionStorage.getItem(item)));
								sessionStorage.removeItem(item);
							});
							deferred.resolve(items);
							document.body.removeChild(fragment);
						}
					});
					node.style.display = 'none';
					fragment.appendChild(node);
				});
				fragment.style.display = 'none';
				document.body.appendChild(fragment);
			}
			return deferred;
		};
	}
}(jQuery));
