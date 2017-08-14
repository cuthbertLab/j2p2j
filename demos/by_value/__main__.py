try:
    import j2p2j
except ImportError:
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    import j2p2j


class MyClient(j2p2j.Client):
    class_events = [
        { "element": "#incrementButtons button",
          "event": "click",
          "method": "increment",
         },
    ]

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

    def increment(self, to_increment, element):
        print('increment called')
        original_value = int(to_increment)
        if element == "#one":
            return original_value + 1
        if element == "#ten":
            return original_value + 10
        if element == "#twenty":
            return original_value + 20

    def increment_update(self, val):
        return self.update(val)

if __name__ == '__main__':
    a = j2p2j.Application('appFiles/index.html', MyClient)
    a.run()
