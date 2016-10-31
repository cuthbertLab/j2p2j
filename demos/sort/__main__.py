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

    def sort(self, first):
        nums = [int(element) for element in first]
        nums.sort()
        '''
        if first > second:
            answer = str(second) + ", " + str(first)
        else:
            answer = str(first) + ", " + str(second)
        '''
        return {'answer': nums}

if __name__ == '__main__':
    a = MyApp('appFiles/index.html', MyClient)
    a.run()