import socket
import sys

from event_app import EventsApp


class SocketServerApp(EventsApp):

    def __init__(self, host, port):
        super(SocketServerApp,self).__init__()
        self._host = host
        self._port = port
        self._clients = []

        self._rsvpSkt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._rsvpSkt.bind( (host, port) )
        self._rsvpSkt.listen(0)
        print "RSVP SOCKET: %s" % repr(self._rsvpSkt.getsockname())
    
        self.add_channel(self._rsvpSkt, self.COND_READ, self.accept_client)

    def accept_client(self, event):
        commSkt, commAddr = self._rsvpSkt.accept()
        print "New Connection from: socket=%s addr=%r" % (commSkt, commAddr)

        self._clients.append(commSkt)
        self.add_channel(commSkt, self.COND_READ, self.read_client)

    def read_client(self, event):
        client_chan = event.channel()
        print 'CHAN %s' % client_chan
        msg = client_chan.recv(8192)
        if not msg:
            print 'EOF: %r' % (client_chan.getpeername(),)
            self.remove_channel(event.eid())
            self._clients.remove(client_chan)
            client_chan.close()
            return
            
        print 'READ(%s): %r' % (client_chan.getpeername(), msg)
        client_chan.send(msg)
        

if __name__ == '__main__':
    if len(sys.argv) == 2:
        addr = sys.argv[1].split(':')
        if len(addr) == 2:
            host, port = addr[0], int(addr[1])
        elif len(addr) == 1:
            host, port = '', int(addr[0])
        else:
            print 'Invalid server address option: %r' % sys.argv[1]
    else:
        host, port = '', 0

    app = SocketServerApp(host, port)
    app.main_loop()
