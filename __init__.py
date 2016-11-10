# -*- coding: utf-8 -*-
import inspect
import os
import sys
import json
import types
import webbrowser
import copy

import tornado.ioloop
import tornado.web
import tornado.options
import tornado.websocket
import tornado.queues

from tornado import gen

class Application(object):
    defaultJ2p2jHead = '''
    <meta http-equiv="X-UA-Compatible" content="chrome=1">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="/static/components/require/require.js" data-main='/static/components/j2p2j' type="text/javascript" charset="utf-8"></script>
    <script>
      require.config({
          baseUrl: '/static/components/',
          paths: {
            jquery : '/static/components/jquery/jquery-2.1.1.min',
          },
      });
    </script>
    '''
    
    def __init__(self, htmlStart="index.html", clientClass=None):
        self.htmlStart = htmlStart
        self.port = 8888
        self.staticName = 'static'
        self._dirName = ''
        self._j2p2jDirName = ''
        self.checkOrigin = True
        self.clients = {}
        if clientClass is None:
            clientClass = Client
        self.clientClass = clientClass
        self._clientMethods = []
        self.j2p2jHead = self.defaultJ2p2jHead
        
        self.debug = True
    ## properties ##
    
    def _getHTMLStart(self):
        if os.path.isabs(self._htmlStart): 
            return self._htmlStart
        else:
            argStart = sys.argv[0]
            if not os.path.isabs(argStart):
                argStart = os.getcwd() + os.sep + argStart
                if not os.path.isdir(argStart):
                    argStart = os.path.dirname(argStart)
            else:
                if argStart.endswith('.py') or argStart.endswith('.pyc'):
                    argStart = os.path.dirname(argStart)                    
            return argStart + os.sep + self._htmlStart
        
    def _setHTMLStart(self, htmlStart):
        self._htmlStart = htmlStart
        
    htmlStart = property(_getHTMLStart, _setHTMLStart)
    
    def _getDirName(self):
        if (self._dirName == ""):
            return os.path.dirname(inspect.getmodule(self.__class__).__file__)
        else:
            return self._dirName
        
    def _setDirName(self, dirName):
        self._dirName = dirName
        
    dirName = property(_getDirName, _setDirName)
    
    def _getJ2P2JDirName(self):
        if (self._j2p2jDirName == ""):
            return os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        else:
            return self._j2p2jDirName
        
    def _setJ2P2JDirName(self, dirName):
        self._j2p2jDirName = dirName

    j2p2jDirName = property(_getJ2P2JDirName, _setJ2P2JDirName)
    
    
    def _getClientMethods(self):
        if len(self._clientMethods) > 0:
            return self._clientMethods
        cm = dir(self.clientClass)
        _clientMethods = []
        for m in cm:
            if m.startswith('_'):
                pass
            _clientMethods.append(m)
        self._clientMethods = _clientMethods
        return _clientMethods

    def _setClientMethods(self, cm):
        self._clientMethods = cm
    
    clientMethods = property(_getClientMethods, _setClientMethods)
    
    ## Client Methods ##
    def createClient(self, clientId=None): 
        c = self.clientClass()
        c.id = clientId
        c.application = self
        return c

    ## Start Methods ##
    def run(self):
        self.setupHandlers()
        self.startServer()
        
    def startServer(self):
        tornado.options.define("port", default=self.port, help="run on the given port", type=int)
        tornadoApp = tornado.web.Application(self.tornadoHandlers)
        
        #tornado.options.parse_command_line()
        tornadoApp.listen(tornado.options.options.port)
        iolooper = tornado.ioloop.IOLoop.instance()
        print("Tornado Started")
        webbrowser.open("http://localhost:8888")
        iolooper.start()

    
    def setupHandlers(self):
        ## todo -- take from ApplicationClass...
        j2p2jDirName = self.j2p2jDirName
        staticPath = os.path.join(j2p2jDirName, self.staticName)
        tornadoHandlers = [
            (r'/', IndexHandler, {'options': {'htmlStart': self.htmlStart, 'j2p2j': self}}),
            (r'/ws', MyWebSocketHandler, {'options': {'j2p2j': self}}),
            (r'/static/(.*)', IndexAwareStaticFileHandler, {'path': staticPath})
        ]
        self.tornadoHandlers = tornadoHandlers
        return tornadoHandlers
    
    
    def runOld(self):
        '''
        run the Javascript to Python processor
        '''

        relativeStaticFile = self.staticName + os.sep + self.htmlStart
        relativeBlankFile = self.staticName + os.sep + 'blankTemplate.html'
        relativeIndexFile = self.staticName + os.sep + 'index.html'

        with open(relativeStaticFile) as f:
            allLines = f.read()
        
        with open(relativeBlankFile) as f:
            templateFile = f.read()
            
        outputtedFileCode = templateFile + allLines + "\n<!-- end User Code -->\n</body></html>"

        with open(relativeIndexFile, 'w') as f:
            f.write(outputtedFileCode)
        
####
class Client(object):

    class_events = []

    def __init__(self):
        self.message = ""
        self.newMessage = False
        self.millisecondsToWait = 1
        self.events = copy.deepcopy(self.class_events)

    def register(self):
        return {
            "method": "REGISTER",
            "events": self.events
        }

    @gen.coroutine
    def get(self, to_send):
        self.send_message(to_send)
        #newMessage or client disconnected
        while not self.newMessage:
            yield gen.sleep(self.millisecondsToWait /  1000)
        self.newMessage = False
        return self.message

    def get_response(self, json):
        self.message = json
        self.newMessage = True
        return {}

    @gen.coroutine
    def process_command(self, send_routine, command, originElement):
        print("Processing")
        print(command)
        if command == "register":
            print("register acitvated")
            send_routine(self.register())
        elif command.startswith("_"):
            return

        #handle
        bound_command_read = getattr(self, command + '_read', None)
        bound_command = getattr(self, command, None)
        bound_command_update = getattr(self, command + '_update', None)

        if bound_command_read is not None:
            print("Read exists")
            readMessage = bound_command_read()
            print(readMessage)
            readReply = yield self.get(readMessage)
            print(readReply)
        else:
            readReply = None

        response = bound_command(readReply, originElement)

        if bound_command_update is not None:
            print("update exists")
            update_message = bound_command_update(response)
            send_routine(update_message)

        return {}
####
class IndexHandler(tornado.web.RequestHandler):
    def initialize(self, options=None):
        self.options = options
        if (options is not None and 'htmlStart' in options):
            self.htmlStart = options['htmlStart']
        else:
            self.htmlStart = 'index.html'  
        if (options is not None and 'j2p2j' in options):
            self.j2p2j = options['j2p2j']
        
    @tornado.web.asynchronous
    def get(self, **kwargs):
        #self.write("This is your response")
        #if "Id" in kwargs.keys():
        #    print("Your client id is: %s" % (kwargs["Id"],))
        self.render(self.htmlStart, j2p2jHead=self.j2p2j.j2p2jHead)
        #self.finish()


class MyWebSocketHandler(tornado.websocket.WebSocketHandler):
    def initialize(self, options=None):
        self.options = options
        if (options is not None and 'j2p2j' in options):
            self.j2p2j = options['j2p2j']
            self._check_origin = self.j2p2j.checkOrigin
               
    def open(self, *args):
        self.id = self.get_argument("clientId")
        self.stream.set_nodelay(True)

        c = self.j2p2j.createClient(self.id)
        self.client = c
        self.j2p2j.clients[self.id] = c
 
    def on_message(self, message):
        if "send_message" not in dir(self.client):
            self.client.send_message = self.send_message
        messageObj = json.loads(message)
        print("Received: " + message);
        if ('newMethod' in messageObj):
            command = messageObj['newMethod']
            if 'originElement' in messageObj:
                element = messageObj['originElement']
            else:
                element = None
            print("before process")
            response = self.client.process_command(self.send_message, command, element)
            print("after process")
            if not isinstance(response, tornado.concurrent.Future):
                responseJson = json.dumps(response)
                fut = self.send_message(response)
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
                responseBundle['error'] += ': ' + messageObj['method'];
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
            print("Client %s received a message: %r, so I sent a reply: %r" % (self.id, message, responseJson))
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

    
## from Mike H  -- http://stackoverflow.com/questions/14385048/is-there-a-better-way-to-handle-index-html-with-tornado
class IndexAwareStaticFileHandler(tornado.web.StaticFileHandler):
    def parse_url_path(self, url_path):
        if not url_path or url_path.endswith('/'):
            url_path += 'index.html'

        return super(IndexAwareStaticFileHandler, self).parse_url_path(url_path)
    
    