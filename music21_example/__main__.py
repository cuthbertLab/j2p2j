import j2p2j
import logging
from tornado import gen
from music21 import *

class MyClient(j2p2j.Client):
    def __init__(self):
        super().__init__()
        self.events2Register = [
            {"element": "#key_up", "event": "click", "method":"key_up"},
            {"element": "#key_down", "event": "click", "method":"key_down"}
        ]
        print('events registered')

    def key_up(self):
        print('key_up')
        self.key_change(1)

    def key_down(self):
        print('key_down')
        self.key_change(-1)

    @gen.coroutine
    def key_change(self, value):
        print('running key change')
        inputs = yield self.DOM.read("input", "attribute", "value")
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
            self.DOM.update("input:nth-child(" + str(idx + 1) + ")",
                            "attributes", {"value": str(val).replace("-", "b")})

if __name__ == '__main__':
    server = j2p2j.Application('templates/index.html', MyClient)
    server.run()
