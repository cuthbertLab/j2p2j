# -*- coding: utf-8 -*-
import inspect
import os
import sys
import json

import tornado.ioloop
import tornado.web
import tornado.options
import tornado.websocket

class Application(object):
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
    ## properties ##
    
    def _getHTMLStart(self):
        if os.path.isabs(self._htmlStart): 
            return self._htmlStart
        else:
            return os.path.dirname(sys.argv[0]) + os.sep + self._htmlStart
        
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
        iolooper.start()
    
    def setupHandlers(self):
        ## todo -- take from ApplicationClass...
        j2p2jDirName = self.j2p2jDirName
        staticPath = os.path.join(j2p2jDirName, self.staticName)
        tornadoHandlers = [
            (r'/', IndexHandler, {'options': {'htmlStart': self.htmlStart}}),
            (r'/ws', MyWebSocketHandler, {'options': {'application': self}}),
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
    pass
    
####
class IndexHandler(tornado.web.RequestHandler):
    def initialize(self, options=None):
        self.options = options
        if (options is not None and 'htmlStart' in options):
            self.htmlStart = options['htmlStart']
        else:
            self.htmlStart = 'index.html'  
        
    @tornado.web.asynchronous
    def get(self, **kwargs):
        #self.write("This is your response")
        #if "Id" in kwargs.keys():
        #    print("Your client id is: %s" % (kwargs["Id"],))
        self.render(self.htmlStart)
        #self.finish()


class MyWebSocketHandler(tornado.websocket.WebSocketHandler):
    def initialize(self, options=None):
        self.options = options
        if (options is not None and 'application' in options):
            self.application = options['application']
            self._check_origin = self.application.checkOrigin
               
    def open(self, *args):
        self.id = self.get_argument("clientId")
        self.stream.set_nodelay(True)

        c = self.application.createClient(self.id)
        self.client = c
        self.application.clients[self.id] = c
 
    def on_message(self, message):
        messageObj = json.loads(message)
        if ('messageId' in messageObj):
            messageId = messageObj['messageId']
        else:
            messageId = 0
        responseBundle = {'messageId': messageId}
        
        method = None
        if ('method' in messageObj):
            method = messageObj['method']
            if method not in self.application.clientMethods:
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
                responseBundle['response'] = response
            except Exception as e:
                responseBundle['error'] = repr(e)
        
        responseJson = json.dumps(responseBundle)
        print("Client %s received a message: %r, so I sent a reply: %r" % (self.id, message, responseJson))
        self.write_message(responseJson)
 
    def on_close(self):
        self.client.application = None
        if self.id in self.application.clients:
            del self.application.clients[self.id]
        del self.client
        del self.application
        
    def check_origin(self, origin):
        if (callable(self._check_origin)):
            return self._check_origin(origin)
        else:
            return self._check_origin
    
## from Mike H  -- http://stackoverflow.com/questions/14385048/is-there-a-better-way-to-handle-index-html-with-tornado
class IndexAwareStaticFileHandler(tornado.web.StaticFileHandler):
    def parse_url_path(self, url_path):
        if not url_path or url_path.endswith('/'):
            url_path += 'index.html'

        return super(IndexAwareStaticFileHandler, self).parse_url_path(url_path)
    
    
    
if __name__ == '__main__':
    a = Application('static/blankTornado.html')
    a.run()