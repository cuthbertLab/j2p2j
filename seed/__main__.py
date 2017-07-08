from j2p2j import Client, Application
from tornado import gen
    
class MyApp(Application):
    pass

class MyClient(Client):
    def __init__(self):
        super(MyClient, self).__init__()
        self.counter = 0
        self.boxes = []
        self.events2Register = [
            {"element":"#add_new_box", "event": "click","method":"addBox"},
            {"element":"#delete_last_box", "event": "click","method":"delete_last_box"},
            {"element":"#add_inputs", "event": "click","method":"addInputs"}
        ]

    @gen.coroutine
    def addInputs(self):
        result = yield self.DOM.read(".inputs", "attribute", "value")
        addition = sum([int(x) for x in list(result)])
        self.DOM.update("#total", "html", addition)

    def addBox(self):
        self.DOM.create("input", "#boxes", {"type":"number","value":"0", "class":"inputs"})

    def delete_last_box(self):
        self.DOM.delete("#boxes input:last-child")

if __name__ == '__main__':
    server = MyApp('templates/index.html', MyClient)
    server.run()
"""
import j2p2j
from tornado import gen
    
class MyApp(j2p2j.Application):
    def __init__(self):
        super(MyApp, self).__init__()
        self.staticName = 'static'

class MyClient(j2p2j.Client):
    def __init__(self):
        super(MyClient, self).__init__()

    def register(self):
        registerEvents = {
            "method":"REGISTER",
            "events":[]
        }
        return registerEvents

if __name__ == '__main__':
    server = MyApp('templates/index.html', MyClient)
    server.run()
"""