try:
    import j2p2j
except ImportError:
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    import j2p2j
    from tornado import gen
    
class MyApp(j2p2j.Application):
    pass

class MyClient(j2p2j.Client):
    def __init__(self):
        super(MyClient, self).__init__()
        self.counter = 0
        self.boxes = []

    def register(self):
        registerEvents = {
            "method":"REGISTER",
            "events":[
                {"element":"#add_new_box", "event": "click","method":"addBox"},
                {"element":"#delete_last_box", "event": "click","method":"delete_last_box"},
                {"element":"#add_inputs", "event": "click","method":"addInputs"}
            ]
        }
        return registerEvents

    @gen.coroutine
    def addInputs(self):
        print("Getting input value")
        send = {"method": "READ"}
        send["location"] = ".inputs"
        send["toGet"] = "attribute"
        send["get"] = "value"
        result = yield self.get(send)
        addition = sum([int(x) for x in list(result)])
        send = {"method": "UPDATE"}
        send["location"] = "#total"
        send["toChange"] = "html"
        send["edit"] = addition
        print("Updating input")
        return send

    def addBox(self):
        print("adding box")
        send = {"method": "CREATE"}
        send["type"] = "input"
        send["location"] = "#boxes"
        send["attributes"] = {"type":"number","value":"0", "class":"inputs"}
        return send

    def delete_last_box(self):
        send = {"method": "DELETE"}
        send["location"] = "#boxes input:last-child"
        return send

if __name__ == '__main__':
    a = MyApp('appFiles/index.html', MyClient)
    a.run()