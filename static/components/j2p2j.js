define([], () => {
    j2p2j = {websocket: null}
    //j2p2j.port = (window.location.port != "") ? ":" + window.location.port : "";
    j2p2j.websocketHost = 'ws://' + window.location.host; // + j2p2j.port;
    j2p2j.websocketUri = j2p2j.websocketHost + '/ws';
    j2p2j.messageIdCallbacks = {};
    j2p2j.messageIdErrorCallbacks = {};
    
    j2p2j.onopen = function () {j2p2j.sendNew("register")};
    j2p2j.onclose = function () {};
    j2p2j.onmessage = function (evt) {
        var data = JSON.parse(evt.data);
        console.log("Received: ", data);
        if (data.method === "CREATE") {
            var newElement = document.createElement(data.type);
            for (attribute in data.attributes) {
                newElement.setAttribute(attribute, data.attributes[attribute]);
            }
            document.querySelector(data.location).appendChild(newElement);
            return
        }
        if (data.method === "UPDATE") {
            var element = document.querySelector(data.location)
            if (data.toChange === "html") {
                element.innerHTML = data.edit
            } else if (data.toChange === "attributes"){
                for (attribute in data.edit) {
                    if(!element.getAttribute(attribute) || data.edit[attribute] === "") {
                        element.setAttribute(attribute, data.edit[attribute]);
                    } else {
                        element[attribute] = data.edit[attribute];
                    }
                }
            }
            return
        }
        if (data.method === "DELETE") {
            var element = document.querySelector(data.location)
            element.parentNode.removeChild(element);
            return
        }
        if (data.method === "REGISTER") {
            data.events.forEach((event) => {
                var element = document.querySelector(event.element)
                element.addEventListener(event.event, () => {j2p2j.sendNew(event.method)});
            });
            return
        }
        if (data.method === "READ") {
            console.log("GET method used");
            var element = document.querySelector(data.location)
            if (data.toGet === "html") {
                console.log("Telling python to handle response")
                j2p2j.send("get_response", [element.innerHTML])
            } else if (data.toGet === "attribute") {
                console.log("Getting Attributes");
                console.log(data.get);
                j2p2j.send("get_response", [element[data.get]])
            }
            return
        }
        var response = data.response;
        var errorResponse = data.error;
        
        var messageId = data.messageId;
        var callback = j2p2j.messageIdCallbacks[messageId];
        var errorCallback = j2p2j.messageIdErrorCallbacks[messageId];
        
        delete j2p2j.messageIdCallbacks[messageId];
        delete j2p2j.messageIdErrorCallbacks[messageId];

        if (errorResponse !== undefined) {
            // error;
            if (errorCallback !== undefined) {
                errorCallback(errorResponse);
            } else {
                console.error("Server error:", errorResponse);
            }
        }  else {
            if (callback !== undefined) {
                callback(response);
            } else {
                console.log('message received:', response);   
            }            
        }

        //can add the GET, PUT, POST DELETE idea here once we see what the request is
    };
    /**
     * Send takes a very flexible list of up to three arguments which can be
     * objects, strings, functions or arrays.  A typical usage would be
     * 
     * j2p2j.send('methodName', [arg0, arg1], {keywordArg: value}, {callback: callbackFunction, error: errorFunction})
     * 
     * but might be
     * 
     * j2p2j.send({method: 'methodName', callback: function (d) {}, arg: 5})
     * 
     * etc.
     */
    j2p2j.send = function(arg0, arg1, arg2, arg3) {
        var method;
        var singleArg;
        var args;
        var kwargs;
        var callback;
        var error;
        var callArgs = [arg0, arg1, arg2, arg3];
        for (var i = 0; i < callArgs.length; i++) {
            var a = callArgs[i];
            if (typeof a == 'string' && method === undefined) {
                method = a;
            } else if (typeof a == 'object' && a !== null && a.constructor !== Array &&
                        (a.callback === undefined && a.error === undefined &&
                         a.args === undefined && a.arg === undefined && a.kwargs === undefined)) {
                kwargs = a;
            } else if (a !== undefined && a !== null && a.constructor === Array) {
                args = a;
            } else if (typeof a == 'function' && callback === undefined) {
                callback = a;
            } else if (typeof a == 'function' && error === undefined) {
                error = a;
            } else if (typeof a == 'object' && a !== null) {
                if (a.method !== undefined && method === undefined) {
                    method = a.method;
                }
                if (a.arg !== undefined && singleArg === undefined) {
                    singleArg = a.arg;
                }
                if (a.args !== undefined && args === undefined) {
                    args = a.args;
                }
                if (a.kwargs !== undefined && kwargs === undefined) {
                    kwargs = a.kwargs;
                }
                if (a.callback !== undefined && callback === undefined) {
                    callback = a.callback;
                }
                if (a.error !== undefined && error === undefined) {
                    error = a.error;
                }
            }
        }
        if (args === undefined && singleArg !== undefined) {
            args = [singleArg];
        }
        //console.log(method, callback, args, kwargs, error);
        j2p2j.sendRaw(method, callback, args, kwargs, error);
    };
    
    j2p2j.sendRaw = function(method, callback, args, kwargs, error) {
        var msgId = j2p2j.makeMessageId();
        j2p2j.messageIdCallbacks[msgId] = callback;
        j2p2j.messageIdErrorCallbacks[msgId] = error;

        var msg = {messageId: msgId, method: method};
        if (args !== undefined) {
            msg.args = args;
        }
        if (kwargs !== undefined) {
            msg.kwargs = kwargs;
        }
        var jsonMsg = JSON.stringify(msg);
        console.log("Sending Raw: ", jsonMsg);     
        j2p2j.websocket.send(jsonMsg);
    }
    j2p2j.sendNew = function(method) {
        var msg = {newMethod:method}
        var jsonMsg = JSON.stringify(msg);
        console.log("Sending New: ", jsonMsg);
        j2p2j.websocket.send(jsonMsg);
    }
    j2p2j.makeMessageId = function () {
        return ((Date.now()) * 1000) + Math.floor(Math.random() * 1000);
    };
    
    j2p2j.connect = function(id, options) {
        if (id === undefined) {
            id = 12345678;
        }
        var WSClass;
        if (typeof(WebSocket) !== 'undefined') {
            WSClass = WebSocket;
        } else if (typeof(MozWebSocket) !== 'undefined') {
            WSClass = MozWebSocket;
        } else {
            alert('Your browser does not have WebSocket support, please try a recent version of Chrome, Safari or Firefox, or IE 10+.');
        }
        ws = new WSClass(this.websocketUri + "?clientId=" + id.toString());
        if (options !== undefined && options.onopen !== undefined) {
            ws.onopen = options.onopen;
        } else {
            ws.onopen = j2p2j.onopen;            
        }
        ws.onmessage = j2p2j.onmessage;
        if (options !== undefined && options.onclose !== undefined) {
            ws.onclose = options.onclose;
        } else {
            ws.onclose = j2p2j.onclose;            
        }
        j2p2j.websocket = ws;
    }


    // var get =  function(elementID, request, attribute) {
    //     var element = $(elementID)
    //     if (request === "html") {
    //          return element.html();
    //     } else if (request === "attribute") {
    //         return element.attr(attribute);
    //     }
    // }



    return j2p2j;
});