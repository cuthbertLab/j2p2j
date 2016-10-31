try:
    import j2p2j
except ImportError:
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    import j2p2j
    
class MyApp(j2p2j.Application):
    pass

class MyClient(j2p2j.Client):
    def __init__(self):
        self.counter = 0

    def register(self):
        registerEvents = {
            "method":"REGISTER",
            "events":[
                {"element":"#add_new_box", "event": "click","method":"addBox"},
                {"element":"#delete_last_box", "event": "click","method":"delete_last_box"}
            ]
        }
        return registerEvents

    def addBox(self):
        send = {"method": "CREATE"}
        send["type"] = "input"
        send["location"] = "#boxes"
        send["attributes"] = {"type":"number","value":"0"}
        return send

    def delete_last_box(self):
        send = {"method": "DELETE"}
        send["location"] = "#boxes input:last-child"
        return send

if __name__ == '__main__':
    a = MyApp('appFiles/index.html', MyClient)
    a.run()