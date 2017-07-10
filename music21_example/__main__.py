from j2p2j import Client, Application
from tornado import gen
from music21 import *
    
class MyApp(Application):
    pass

class MyClient(Client):
    def __init__(self):
        self.events2Register = [
            {"element":"#key_up", "event": "click","method":"key_up"},
            {"element":"#key_down", "event": "click","method":"key_down"}
        ]

    def key_up(self):
        self.key_change(1)

    def key_down(self):
        self.key_change(-1)

    @gen.coroutine
    def key_change(self, value):
        inputs = yield self.DOM.read("input","attribute","value")
        s = stream.Stream()
        for input in inputs:
            i = list(input)
            if i[-2] == "b" and len(i) > 2:
                i[-2] = "-"
            s.append(note.Note("".join(i)))
        print([str(p) for p in s.pitches])
        for n in s.recurse().notes:
            n.transpose(value, inPlace=True)
        print([str(p) for p in s.pitches])
        for idx, val in enumerate(s.pitches):
            print(idx)
            self.DOM.update("input:nth-child("+str(idx+1)+")", "attributes", {"value":str(val).replace("-","b")})

if __name__ == '__main__':
    server = MyApp('templates/index.html', MyClient)
    server.run()