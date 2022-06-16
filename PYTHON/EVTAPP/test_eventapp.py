import socket
import sys

import sim_runtachyon as eventapp



def Timeout1(to_entry):
    print('Timeout1 id=%s data=%s' % (to_entry.id(),to_entry.userdata()))
    to_entry.app().add_timeout(3000, Timeout2, 'TO2-DATA')
    to_entry.app().add_timeout(4000, Timeout3, 'TO3-DATA')


def Timeout2(to_entry):
    print('Timeout2 id=%s data=%s' % (to_entry.id(),to_entry.userdata()))

def Timeout3(to_entry):
    print('Timeout3 id=%s data=%s' % (to_entry.id(),to_entry.userdata()))
    
def Timeout4(to_entry):
    print('Timeout4 id=%s data=%s' % (to_entry.id(),to_entry.userdata()))

def TimeoutCancel(to_entry):
    print('TimeoutCancel id=%s data=%s' % (to_entry.id(),to_entry.userdata()))
    msg, to_id = to_entry.userdata()
    removed = to_entry.app().remove_timeout(to_id)
    print('Removed timeout status=%s id=%s' % (removed,to_id))

def comm_readable(chan_entry):
    print('comm_readable: fd=%s' % chan_entry.channel().fileno())
    comm_in = chan_entry.channel().recv(4096)
    if comm_in:
        chan_entry.channel().send(comm_in)
    else:
        chan_entry.app().remove_channel(chan_entry.id())
    
def rsvp_readable(chan_entry):
    print('rsvp_readable: fd=%s' % chan_entry.channel().fileno())
    app = chan_entry.app()
    
    comm_sock, comm_addr = chan_entry.channel().accept()
    print('COMM SOCK: %s' % repr(comm_addr))
    app.add_channel(comm_sock, app.COND_READ, comm_readable,
                    'COMM-%s' % comm_sock.fileno())
    
if __name__ == '__main__':
    
    app = eventapp.EventsApp()

    app.add_timeout(3000, Timeout1, 'TO1-DATA')

    to4_id = app.add_timeout(10000, Timeout4, 'TO4-DATA')
    app.add_timeout(3000, TimeoutCancel, ('TO-DATA', to4_id))

    
    rsvp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    rsvp_sock.bind(('0.0.0.0', 0))
    print('RSVP SOCKET: %s' % repr(rsvp_sock.getsockname()))
    rsvp_sock.listen(5)

    chan_id = app.add_channel(rsvp_sock, app.COND_READ, rsvp_readable, None)
    print('RSVP CHAN ID: %s' % chan_id)
    
    app.main_loop()
    
