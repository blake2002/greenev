import select
import socket
import greenlet
import time

class SelectServer(object):
    def __init__(self, port):
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serversocket.bind(('0.0.0.0', port))
        self.serversocket.listen(5000)
        self.serversocket.setblocking(0)

    def processRequest(self, request):
        g=greenlet.getcurrent()
        g.parent.switch("Warning: ")
        return "Replace processRequest function in your code.\n"

    def poll(self, timeout=10):
        run_tasks = {}
        indate = {}

        inputs = [self.serversocket,]
        outputs = []

        connections = {}
        requests = {}
        responses = {}

        while True:

            for (fileno, task) in run_tasks.items():
                res = task.switch(requests[fileno])
                responses[fileno] += res

            for (fileno, _time) in indate.items():
                if _time < time.time():
                    del run_tasks[fileno]
                    del indate[fileno]
                    responses[fileno] = "Timeout"

            readable , writable , exceptional = select.select(inputs, outputs, inputs, 1)

            for s in readable :
                if s is self.serversocket:
                    try:
                        while True:
                            connection, client_address = s.accept()
                            connection.setblocking(0)
                            inputs.append(connection)
                            connections[connection.fileno()] = connection
                            requests[connection.fileno()] = b""
                            responses[connection.fileno()] = b""
                    except socket.error:
                        pass
                else:
                    while True:
                        try:
                            requests[s.fileno()] += s.recv(1024)
                        except socket.error as e:
                            run_tasks[s.fileno()]=greenlet.greenlet(self.processRequest)
                            if timeout >= 0:
                                indate[s.fileno()] = time.time() + timeout
                            else:
                                pass
                            inputs.remove(s)
                            outputs.append(s)
                            break
            for s in writable:
                try:
                    while len(responses[s.fileno()]) > 0:
                        byteswritten = s.send(responses[s.fileno()])
                        responses[s.fileno()] = responses[s.fileno()][byteswritten:]
                except socket.error:
                    pass
                if len(responses[s.fileno()]) == 0:
                    if fileno not in run_tasks or run_tasks[s.fileno()].dead:
                        try:
                            del run_tasks[s.fileno()]
                            del indate[s.fileno()]
                        except:
                            pass
                        outputs.remove(s)
                        s.shutdown(socket.SHUT_RDWR)
                    else:
                        pass
            for s in exceptional:
                if s in inputs:
                    inputs.remove(s)
                if s in outputs:
                    outputs.remove(s)
                s.close()
