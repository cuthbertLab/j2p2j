try:
    import j2p2j
except ImportError:
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    import j2p2j

from tornado import gen

class MyClient(j2p2j.Client):

    @gen.coroutine
    def push_server(self):
        send = {"method": "READ"}
        send["location"] = "#toEdit"
        send["toGet"] = "html"
        m = yield self.get(send)
        print(m)
        return {}

    def register(self):
        registerEvents = {
            "method": "REGISTER",
            "events":[
                {"element": "#pushServer",
                "event": "click",
                "method": "push_server"}
            ]
        }
        return registerEvents

if __name__ == '__main__':
    a = j2p2j.Application('appFiles/index.html', MyClient)
    a.run()
