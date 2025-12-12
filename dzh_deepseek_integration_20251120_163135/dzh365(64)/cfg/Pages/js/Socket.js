var Socket = {
    root:window.external && external.wsroot ? external.wsroot : 'ws://127.0.0.1:30718',
    queue:[],
    callbacks:{},
    waiting:false,
    instance:function () {
        if (this._instance === undefined) {
            var me = this,
                events = ['open', 'message', 'error', 'close'];
            this._instance = new WebSocket(this.root);
            events.forEach(function (item) {
                me._instance.addEventListener(item, me);
            });
            addEventListener('unload', function () {
                me._instance.close();
                events.forEach(function (item) {
                    me._instance.removeEventListener(item, me);
                });
                removeEventListener('unload', arguments.callee);
            });
        }
        return this._instance;
    },
    handleEvent:function (e) {
        e.type in this && this[e.type](e);
    },
    send:function (url, callback) {
        this.queue.push([url, callback]);
        if (!this.waiting && this.instance().readyState === 1) {
            this.waiting = true;
            this.subscribe();
        }
    },
    subscribe:function () {
        this.instance().send('/json/subscribe?' + this.queue[0][0]);
    },
    open:function (e) {
        this.queue.length && this.subscribe();
    },
    error:function (e) {
        if (this.queue.length) {
            this.queue.push(this.queue.shift());
            this.subscribe();
        }
    },
    message:function (e) {
        var data = JSON.parse(e.data);
        if (data.res_seq === '0') {
            if (this.queue.length) {
                this.callbacks[data.req_seq] = this.queue.shift()[1];
            }
            if (this.queue.length) {
                this.subscribe();
            } else {
                this.waiting = false;
            }
        } else {
            if (data.req_seq > 0 && data.req_seq in this.callbacks) {
                if (data.res_type >= 0 && data.result && data.result.datas && data.result.head) {
                    var items = [],
                        rows = data.result.datas,
                        rl = rows.length,
                        cols = data.result.head,
                        cl = cols.length;
                    for (var i = 0; i < rl; i++) {
                        var row = rows[i],
                            item = {};
                        for (var j = 0; j < cl; j++) {
                            item[cols[j]] = row[j];
                        }
                        items.push(item);
                    }
                    this.callbacks[data.req_seq](items);
                } else {
                    this.callbacks[data.req_seq]([]);
                }
                delete this.callbacks[data.req_seq];
            }
        }
    },
    close:function () {
        this.queue.length = 0;
        for (var key in this.queue.callbacks) {
            delete this.queue.callbacks[key];
        }
    }
};