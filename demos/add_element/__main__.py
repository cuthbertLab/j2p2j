try:
    import j2p2j
except ImportError:
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    import j2p2j


class MyClient(j2p2j.Client):
    def register(self):
        registerEvents = {
            "method":"REGISTER",
            "events":[
                {"element": "#add_new_box",
                 "event": "click",
                 "method": "addBox"}
            ]
        }
        return registerEvents

    def addBox(self):
        send = {"method": "CREATE"}
        send["type"] = "input"
        send["location"] = "#boxes"
        send["attributes"] = {
            "type": "number",
            "value": "0",
        }
        return send

if __name__ == '__main__':
    a = j2p2j.Application('appFiles/index.html', MyClient)
    a.run()
