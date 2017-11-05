import copy
import tornado.queues
import tornado.concurrent

from tornado import gen

class Client:
    '''
    EVENTS:

    Either the class can define "class_events" which all members
    of the class will inherit or they can be returned from the
    "register" function.
    '''

    class_events = []

    def __init__(self):
        self.message = ""
        self.newMessage = False
        self.millisecondsToWait = 1
        self.events = copy.deepcopy(self.class_events)
        self.id = None
        self.application = None

    def register(self):
        return {
            "method": "REGISTER",
            "events": self.events
        }

    @gen.coroutine
    def get(self, to_send):
        self.send_message(to_send)
        #newMessage or client disconnected
        while not self.newMessage:
            yield gen.sleep(self.millisecondsToWait /  1000)
        self.newMessage = False
        return self.message

    def get_response(self, *jsonReceived):
        self.message = jsonReceived
        self.newMessage = True
        return {}

    @gen.coroutine
    def process_command(self, send_routine, command, originElement):
        print("Processing")
        print(command)
        if command == "register":
            print("register acitvated")
            send_routine(self.register())
            return
        elif command.startswith("_"):
            #add debug. exception?
            return

        #handle
        bound_command_read = getattr(self, command + '_read', None)
        bound_command = getattr(self, command, None)
        bound_command_update = getattr(self, command + '_update', None)

        if bound_command_read is not None:
            print("Read exists")
            readMessage = bound_command_read()
            print(readMessage)
            readReply = yield self.get(readMessage)
            print(readReply)
        else:
            readReply = None

        response = bound_command()
        if (isinstance(response, tornado.concurrent.Future)):
            res = yield response
            send_routine(res)
        else:
            send_routine(response)

        if bound_command_update is not None:
            print("update exists")
            update_message = bound_command_update(response)
            send_routine(update_message)

        return {}
