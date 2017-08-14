try:
    import j2p2j
except ImportError:
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    import j2p2j

class MyClient(j2p2j.Client):
    def __init__(self):
        super().__init__()
        self.counter = 0

    def register(self):
        registerEvents = {
            "method":"REGISTER",
            "events":[
                { "element": "#increment",
                  "event": "click",
                  "method": "increment",
                },
                { "element": "#addClass",
                  "event": "click",
                  "method": "add_red_class",
                },
                { "element": "#removeClass",
                  "event": "click",
                  "method": "remove_red_class",
                },
            ]
        }
        return registerEvents

    def increment(self):
        send = {"method": "UPDATE"}
        send["location"] = "#toEdit"
        send["toChange"] = "html"
        self.counter += 1
        send["edit"] = self.counter
        return send

    def _changeClass(self, classAttribute):
        send = {"method": "UPDATE"}
        send["location"] = "#toEdit"
        send["toChange"] = "attributes"
        send["edit"] = {"class": classAttribute}
        return send

    def add_red_class(self):
        return self._changeClass('red')

    def remove_red_class(self):
        return self._changeClass('')

if __name__ == '__main__':
    a = j2p2j.Application('appFiles/index.html', MyClient)
    a.run()
