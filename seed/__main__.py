from j2p2j import Client, Application
from tornado import gen
    
class MyApp(Application):
    pass

class MyClient(Client):
    def __init__(self):
        self.events2Register = []

if __name__ == '__main__':
    server = MyApp('templates/index.html', MyClient)
    server.run()