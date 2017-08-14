import inspect
import os
import sys
import webbrowser

import tornado.ioloop
import tornado.options
import tornado.web

from . import client
from . import tornadoHandlers

class Application:
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
        self._htmlStart = None
        self.htmlStart = htmlStart

        self.port = 8888
        self.staticName = 'static'
        self._dirName = ''
        self._j2p2jDirName = ''
        self.checkOrigin = True
        self.clients = {}
        if clientClass is None:
            clientClass = client.Client

        self.clientClass = clientClass
        self._clientMethods = []
        self.tornadoHandlers = []
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
            return os.path.dirname(
                    os.path.dirname(
                    os.path.abspath(
                    inspect.getfile(
                    inspect.currentframe()))))
        else:
            return self._j2p2jDirName

    def _setJ2P2JDirName(self, dirName):
        self._j2p2jDirName = dirName

    j2p2jDirName = property(_getJ2P2JDirName, _setJ2P2JDirName)


    def _getClientMethods(self):
        if self._clientMethods:
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
        webbrowser.open("http://localhost:" + str(tornado.options.options.port))
        iolooper.start()


    def setupHandlers(self):
        ## todo -- take from ApplicationClass...
        j2p2jDirName = self.j2p2jDirName
        staticPath = os.path.join(j2p2jDirName, self.staticName)
        print(staticPath)
        appTornadoHandlers = [
            (r'/',
             tornadoHandlers.IndexHandler,
             {'options': {
                            'htmlStart': self.htmlStart,
                            'j2p2j': self,
                         }
             }
            ),
            (r'/ws',
             tornadoHandlers.MyWebSocketHandler,
             {'options': {
                          'j2p2j': self
                          }
             }
            ),
            (r'/static/(.*)',
             tornadoHandlers.IndexAwareStaticFileHandler,
             {'path': staticPath}
            )
        ]
        self.tornadoHandlers = appTornadoHandlers
        return appTornadoHandlers
