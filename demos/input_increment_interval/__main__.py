try:
    import j2p2j
except ImportError:
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    import j2p2j

import random
from tornado import gen


class MyClient(j2p2j.Client):
    def __init__(self):
        super().__init__()
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
        randomMax = 20
        if self.incrementValue > 20:
            randomMax = self.incrementValue + 5

        after = {"method": "UPDATE"}
        after["location"] = "#random"
        after["toChange"] = "html"
        after["edit"] = random.randint(self.incrementValue, randomMax)
        return after

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
