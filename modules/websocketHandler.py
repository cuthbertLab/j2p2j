import json
import tornado.websocket

class J2P2JWebSocketHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.id = None
        self.client = None

    def initialize(self, options=None):
        print('J2P2JWebSocketHandler, initialize')

        self.options = options

        if (options is not None and 'j2p2j' in options):
            self.j2p2j = options['j2p2j']
            self._check_origin = self.j2p2j.checkOrigin

    def open(self, *args):
        print('J2P2JWebSocketHandler, open')

        self.id = self.get_argument("clientId")
        self.stream.set_nodelay(True)

        c = self.j2p2j.createClient(self.id)
        self.client = c
        self.j2p2j.clients[self.id] = c

    def on_message(self, message):
        if "send_message" not in dir(self.client):
            self.client.send_message = self.send_message
        messageObj = json.loads(message)
        print("Received: " + message)
        if ('newMethod' in messageObj):
            command = messageObj['newMethod']
            if 'originElement' in messageObj:
                element = messageObj['originElement']
            else:
                element = None
            #change process
            response = self.client.process_command(self.send_message, command, element)
            if not isinstance(response, tornado.concurrent.Future):
                responseJson = json.dumps(response)
                unused_future = self.send_message(response)
            return

        #here we can handle the message for calback, mostly handled alread here
        messageObj = json.loads(message)
        if ('messageId' in messageObj):
            messageId = messageObj['messageId']
        else:
            messageId = 0
        responseBundle = {'messageId': messageId}

        method = None
        if ('method' in messageObj):
            method = messageObj['method']
            if method not in self.j2p2j.clientMethods:
                method = None

        if method is None:
            responseBundle['error'] = 'Unknown method.' # TODO: send error
            if ('method' in messageObj):
                responseBundle['error'] += ': ' + messageObj['method']
        else:
            args = None
            if ('args' in messageObj):
                args = messageObj['args']

            kwargs = None
            if ('kwargs' in messageObj):
                kwargs = messageObj['kwargs']
            boundMethod = getattr(self.client, method)

            try:
                if args is not None and kwargs is not None:
                    response = boundMethod(*args, **kwargs)
                elif args is not None:
                    response = boundMethod(*args)
                elif kwargs is not None:
                    response = boundMethod(**kwargs)
                else:
                    response = boundMethod()

                ## methods can return their own callbacks...
                if isinstance(response, dict) and 'callback' in response:
                    responseBundle['callback'] = response['callback']
                    del response['callback']
                responseBundle['response'] = response
            except Exception as e:
                responseBundle['error'] = repr(e)

        responseJson = json.dumps(responseBundle)
        if self.j2p2j.debug:
            print("Client %s received a message: %r, so I sent a reply: %r" %
                    (self.id, message, responseJson))
        self.write_message(responseJson)

    def on_close(self):
        self.client.application = None
        if self.id in self.j2p2j.clients:
            del self.j2p2j.clients[self.id]
        del self.client
        del self.j2p2j

    def check_origin(self, origin):
        if callable(self._check_origin):
            return self._check_origin(origin)
        else:
            return self._check_origin

    def send_message(self, message):
        responseJson = json.dumps(message)
        print("Sending: " + str(message))
        self.write_message(responseJson)
