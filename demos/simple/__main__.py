try:
    import j2p2j
except ImportError:
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    import j2p2j
    
class MyApp(j2p2j.Application):
    pass

class MyClient(j2p2j.Client):
    def __init__(self):
        self.counter = 0
        
    def increment(self):
        self.counter += 1
        return self.counter

    def multiply(self, first=1, second=1):
        return {'answer': first*second}

if __name__ == '__main__':
    a = MyApp('appFiles/index.html', MyClient)
    a.run()