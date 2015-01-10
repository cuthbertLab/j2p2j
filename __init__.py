# -*- coding: utf-8 -*-
############
#
# IPythonNotebook like connections between Javascript and Python, but 
# start with
# ~/anaconda/bin/python ipyJSapp.py 

# 
#    -- needs ipython v.2  
import os
import threading
import webbrowser
from IPython.html import notebookapp # @UnresolvedImport

j2p2jApp = None

class Application(object):
    def __init__(self, htmlStart="index.html"):
        self.htmlStart = htmlStart
            
    def run(self):
        '''
        run the Javascript to Python processor
        '''
        j2p2jApp = self
        
        thisDirectory = os.path.abspath(os.path.dirname(__file__))
        staticDirectory = os.path.join(thisDirectory, 'static')

        relativeStaticFile = 'static' + os.sep + self.htmlStart
        relativeBlankFile = 'static' + os.sep + 'blankTemplate.html'
        relativeIndexFile = 'static' + os.sep + 'index.html'

        with open(relativeStaticFile) as f:
            allLines = f.read()
        
        with open(relativeBlankFile) as f:
            templateFile = f.read()
            
        outputtedFileCode = templateFile + allLines + "\n<!-- end User Code -->\n</body></html>"

        with open(relativeIndexFile, 'w') as f:
            f.write(outputtedFileCode)
        
        print(relativeStaticFile)
        print(staticDirectory)
        
        npa = notebookapp.NotebookApp()
        npa.extra_static_paths = [staticDirectory]
        #print(npa.connection_url)
        OPEN_IN_NEW_TAB = 2
        
        
        # start the web browser after a delay so that the webserver can already have started...
        delayInSeconds = 2
        startWebbrowserDelayed = lambda: webbrowser.open(
                                        npa.connection_url + relativeIndexFile, new=OPEN_IN_NEW_TAB )
        threading.Timer(delayInSeconds, startWebbrowserDelayed).start()
        
        # now start the main app
        npa.launch_instance(open_browser=False, extra_static_paths = [staticDirectory])
        
        # this runs only after completed...
        print(npa)
        


if __name__ == '__main__':
    a = Application('m21pj.html')
    a.run()
