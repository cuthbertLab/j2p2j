try:
    import j2p2j
except ImportError:
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    import j2p2j

from tornado import gen

class MyClient(j2p2j.Client):

    @gen.coroutine
    def increment(self):
        send = {"method": "READ"}
        send["location"] = "#toIncrement"
        send["toGet"] = "attribute"
        send["get"] = "value"
        m = yield self.get(send)
        print(m)
        after = {"method": "UPDATE"}
        after["location"] = "#toIncrement"
        after["toChange"] = "attributes"
        after["edit"] = {"value": int(m[0]) + 1}
        self.send_message(after)
        return {}


    def register(self):
        registerEvents = {
            "method":"REGISTER",
            "events":[
                { "element": "#increment",
                  "event": "click",
                  "method": "increment",
                },
            ]
        }
        return registerEvents

if __name__ == '__main__':
    a = j2p2j.Application('appFiles/index.html', MyClient)
    a.run()
