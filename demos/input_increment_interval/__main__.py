try:
    import j2p2j
except ImportError:
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    import j2p2j
    from tornado import gen
    import tornado.ioloop
    import random
    
class MyApp(j2p2j.Application):
    pass

class MyClient(j2p2j.Client):
    def __init__(self):
        super(MyClient, self).__init__()
        self.incrementValue = 0

    @gen.coroutine
    def increment(self):
        send = {"method": "READ"}
        send["location"] = "#toIncrement"
        send["toGet"] = "attribute"
        send["get"] = "value"
        m = yield self.get(send)
        self.incrementValue = int(m)
        print(self.incrementValue)
        after = {"method": "UPDATE"}
        after["location"] = "#toIncrement"
        after["toChange"] = "attributes"
        after["edit"] = {"value": self.incrementValue + 1}
        self.send_message(after)
        return {}

    def random(self):
        after = {"method": "UPDATE"}
        after["location"] = "#random"
        after["toChange"] = "html"
        after["edit"] = random.randint(self.incrementValue, 20)
        return after

    def register(self):
        registerEvents = {
            "method":"REGISTER",
            "events":[
                {"element":"#increment", "event": "click","method":"increment"}
            ]
        }
        return registerEvents

if __name__ == '__main__':
    a = MyApp('appFiles/index.html', MyClient)
    a.run()