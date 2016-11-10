try:
    import j2p2j
except ImportError:
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    import j2p2j
    
class MyApp(j2p2j.Application):
    pass

class MyClient(j2p2j.Client):

    class_events = [
        {"element":"#increment", "event": "click", "method": "increment"},
        {"element":"#decrement", "event": "click", "method": "decrement"}
    ]

    def __init__(self):
        super(MyClient, self).__init__()

    def read(self):
        send = {"method": "READ"}
        send["location"] = "#toIncrement"
        send["toGet"] = "attribute"
        send["get"] = "value"
        return send

    def update(self, val):
        after = {"method": "UPDATE"}
        after["location"] = "#toIncrement"
        after["toChange"] = "attributes"
        after["edit"] = {"value": val}
        return after

    def increment_read(self):
        return self.read()

    def increment(self, to_increment):
        return int(to_increment) + 1

    def increment_update(self, val):
        return self.update(val)

    def decrement_read(self):
        return self.read()

    def decrement(self, to_increment):
        return int(to_increment) - 1

    def decrement_update(self, val):
        return self.update(val)


if __name__ == '__main__':
    a = MyApp('appFiles/index.html', MyClient)
    a.run()