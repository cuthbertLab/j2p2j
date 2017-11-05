class J2P2J {
    constructor() {
        this.websocket = null;
        this.websocketHost = 'ws://' + window.location.host;
        this.messageIdCallbacks = {};
        this.messageIdErrorCallbacks = {};
    }

    onopen() {
        this.sendNew('register', null);
    }

    onclose() {}

    onmessage(evt) {
        const data = JSON.parse(evt.data);
        console.log('Received: ', data);
        const dMethod = data.method;
        const methodMap = {
            CREATE: this.create,
            UPDATE: this.update,
            DELETE: this.delete,
            REGISTER: this.register,
            READ: this.read,
        };
        if (methodMap.hasOwnProperty(dMethod)) {
            return methodMap[dMethod](data);
        }

        // fallback -- is this code still used?
        console.log('Calling fallback on ', data);
        const response = data.response;
        const errorResponse = data.error;

        const messageId = data.messageId;
        const callback = this.messageIdCallbacks[messageId];
        const errorCallback = this.messageIdErrorCallbacks[messageId];

        delete this.messageIdCallbacks[messageId];
        delete this.messageIdErrorCallbacks[messageId];

        if (errorResponse !== undefined) {
            // error;
            if (errorCallback !== undefined) {
                errorCallback(errorResponse);
            } else {
                console.error('Server error:', errorResponse);
            }
        } else {
            if (callback !== undefined) {
                callback(response);
            } else {
                console.log('message received:', response);
            }
        }
    }

    create(data) {
        const newElement = document.createElement(data.type);
        for (attribute in data.attributes) {
            newElement.setAttribute(attribute, data.attributes[attribute]);
        }
        document.querySelector(data.location).appendChild(newElement);
        return; // or return newElement?
    }

    update(data) {
        const element = document.querySelector(data.location);
        if (data.toChange === 'html') {
            element.innerHTML = data.edit;
        } else if (data.toChange === 'attributes') {
            for (attribute in data.edit) {
                if (
                    !element.getAttribute(attribute) ||
                    data.edit[attribute] === ''
                ) {
                    element.setAttribute(attribute, data.edit[attribute]);
                } else {
                    element[attribute] = data.edit[attribute];
                }
            }
        }
        return;
    }

    delete(data) {
        const element = document.querySelector(data.location);
        element.parentNode.removeChild(element);
        return;
    }

    register(data) {
        data.events.forEach(eventMapping => {
            const matchingElements = document.querySelector(
                eventMapping.element,
            );
            matchingElements.addEventListener(
                eventMapping.event,
                elementThatEventFiredOn => {
                    this.sendNew(
                        eventMapping.method,
                        eventMapping,
                        elementThatEventFiredOn,
                    );
                },
            );
        });
        return;
    }

    read(data) {
        console.log('READ method used');
        console.log('reading', document.querySelectorAll(data.location));
        const elements = [...document.querySelectorAll(data.location)];
        let response = [];
        if (data.toGet === 'html') {
            console.log('Telling python to handle response');
            if (elements.length > 1) {
                response = elements.map(element => element.innerHTML);
            } else {
                response = [elements[0].innerHTML];
            }
        } else if (data.toGet === 'attribute') {
            console.log('Getting Attributes');
            console.log(data.get);
            console.log(elements[0][data.get]);
            if (elements.length > 1) {
                response = elements.map(element => element[data.get]);
            } else {
                response = [elements[0][data.get]];
            }
        }
        this.send('get_response', response);
        return;
    }

    /**
     * Send takes a very flexible list of up to three arguments which can be
     * objects, strings, functions or arrays.  A typical usage would be
     *
     * j2p2j.send('methodName', [arg0, arg1], {keywordArg: value},
     *            {callback: callbackFunction, error: errorFunction})
     *
     * but might be
     *
     * j2p2j.send({method: 'methodName', callback: function (d) {}, arg: 5})
     *
     * etc.
     */
    send(arg0, arg1, arg2, arg3) {
        let method;
        let singleArg;
        let args;
        let kwargs;
        let callback;
        let error;
        const callArgs = [arg0, arg1, arg2, arg3];
        for (let i = 0; i < callArgs.length; i++) {
            let a = callArgs[i];
            if (typeof a == 'string' && method === undefined) {
                method = a;
            } else if (
                typeof a == 'object' &&
                a !== null &&
                a.constructor !== Array &&
                (a.callback === undefined &&
                    a.error === undefined &&
                    a.args === undefined &&
                    a.arg === undefined &&
                    a.kwargs === undefined)
            ) {
                kwargs = a;
            } else if (
                a !== undefined &&
                a !== null &&
                a.constructor === Array
            ) {
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
        this.sendRaw(method, callback, args, kwargs, error);
    }

    sendRaw(method, callback, args, kwargs, error) {
        msgId = this.makeMessageId();
        this.messageIdCallbacks[msgId] = callback;
        this.messageIdErrorCallbacks[msgId] = error;

        const msg = {messageId: msgId, method: method};
        if (args !== undefined) {
            msg.args = args;
        }
        if (kwargs !== undefined) {
            msg.kwargs = kwargs;
        }
        const jsonMsg = JSON.stringify(msg);
        console.log('Sending Raw: ', jsonMsg);
        this.websocket.send(jsonMsg);
    }
    sendNew(method, eventMapping, elementThatEventFiredOn) {
        const msg = {newMethod: method, eventMapping: eventMapping};
        const jsonMsg = JSON.stringify(msg);
        console.log('Sending New: ', jsonMsg);
        this.websocket.send(jsonMsg);
    }
    makeMessageId() {
        return Date.now() * 1000 + Math.floor(Math.random() * 1000);
    }

    connect(id, options) {
        if (id === undefined) {
            id = 12345678;
        }
        let WSClass;
        if (typeof WebSocket !== 'undefined') {
            WSClass = WebSocket;
        } else if (typeof MozWebSocket !== 'undefined') {
            WSClass = MozWebSocket;
        } else {
            alert(
                'Your browser does not have WebSocket support, please try a recent version of Chrome, Safari or Firefox, or IE 10+.',
            );
            return;
        }

        const ws = new WSClass(
            this.websocketHost + '?clientId=' + id.toString(),
        );
        if (options !== undefined && options.onopen !== undefined) {
            ws.onopen = options.onopen;
        } else {
            ws.onopen = this.onopen;
        }
        ws.onmessage = this.onmessage;
        if (options !== undefined && options.onclose !== undefined) {
            ws.onclose = options.onclose;
        } else {
            ws.onclose = this.onclose;
        }
        this.websocket = ws;
    }
}

define([], () => {
    return new J2P2J();
});
