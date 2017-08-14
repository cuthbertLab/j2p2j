try:
    import j2p2j
except ImportError:
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    import j2p2j

from music21 import corpus
from music21 import freezeThaw
from music21 import note
from music21 import stream

class MyClient(j2p2j.Client):
    def __init__(self):
        super().__init__()
        self.counter = 0
        self.s = corpus.parse('bwv66.6')

    def streamAnalyze(self, nStr):
        s = stream.Stream()
        for ns in nStr.split(","):
            n = note.Note(ns)
            s.append(n)
        return s.analyze("key").sharps

    def getMeasure(self, m, p):
        mobj = self.s.parts[p].measure(m)
        sf2 = freezeThaw.StreamFreezer(mobj)
        return sf2.writeStr(fmt="jsonpickle")

    def increment(self):
        self.counter += 1
        # send = {"method": "UPDATE"}
        # send["location"] = "#mnum"
        # send["toChange"] = "attributes"
        # send["edit"] = {"value":self.counter}
        # return send
        callback = 'function (d) { var n = $("#mnum"); n.val(d.counter) }'
        return {'callback': callback, 'counter': self.counter}


if __name__ == '__main__':
    a = j2p2j.Application('appFiles/index.html', MyClient)
    a.run()
