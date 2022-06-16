import os
import socket
import sys


def test_environ():
    """Test that we can locate TRAM source root."""
    testDir = os.path.dirname(__file__)
    mainDir = os.path.dirname(os.path.dirname(os.path.dirname(testDir)))
    rootDir = os.path.join(mainDir, "src", "python")
    assert rootDir is not None
    assert os.path.isdir(rootDir)
    sys.path.insert(0,rootDir)
  
def test_create_events_app():
    """Test creation of plain EventsApp and EventsApp sub-class>"""
    import  sims.core
    plain_app = sims.core.EventsApp()
    assert plain_app

    class TestEventsApp(sims.core.EventsApp):
        def __init__(self, test_arg):
            super(TestEventsApp,self).__init__()
            self._test_attr = test_arg

    sub_app = TestEventsApp('FOO')
    assert sub_app._test_attr == 'FOO'

def test_single_shot_timeout():
    """Test one half second single shot timeout"""
    import  sims.core
    class SingleShotApp(sims.core.EventsApp):
        def __init__(self):
            super(SingleShotApp,self).__init__()
            self.timer_count = 0
        def single_shot(self, entry):
            print('single shot handler')
            assert entry.userdata() == 'SINGLE'
            self.timer_count += 1
            entry.app().break_main_loop()

    app = SingleShotApp()
    app.add_timeout(500, app.single_shot, 'SINGLE')
    app.main_loop()
    assert app.timer_count == 1

def test_repeating_timeout():
    """Test repeating .2 second timeout"""
    import  sims.core
    class RepeatingApp(sims.core.EventsApp):
        def __init__(self):
            super(RepeatingApp,self).__init__()
            self.timer_count = 0
        def repeat_timeout(self, entry):
            print('repeat handler')
            assert entry.userdata() == 'REPEAT'
            self.timer_count += 1
            if self.timer_count == 3:
                entry.app().break_main_loop()

    app = RepeatingApp()
    app.add_timeout(200, app.repeat_timeout, 'REPEAT', True)
    app.main_loop()
    assert app.timer_count == 3

def test_cancel_timeout():
    """Test the ability to cancel a timer"""
    import sims.core
    class CancelTimerApp(sims.core.EventsApp):
        def __init__(self):
            super(CancelTimerApp,self).__init__()
            self.short_count = 0
            self.long_count  = 0
            self.long_id     = -1
        def long_timeout(self, event):
            print('long_timeout')
            assert 'Should not fire' == 'oops'
        def short_timeout(self, event):
            print('short_timeout')
            self.short_count += 1
            if self.short_count == 1:
                assert event.app().remove_timeout(self.long_id)
            elif self.short_count >= 6:
                event.app().break_main_loop()
                
    app = CancelTimerApp()
    app.long_id = app.add_timeout(500, app.long_timeout)
    app.add_timeout(100, app.short_timeout, 'SHORT', True)
    app.main_loop()

def test_socket_channel():
    """Test socket channel readable behavior"""
    import socket
    import sims.core
    class SocketPairApp(sims.core.EventsApp):
        def __init__(self, sockpair):
            super(SocketPairApp,self).__init__()
            self.sockpair = sockpair
        def read_socket(self, event):
            print('read_socket')
            msg = self.sockpair[0].recv(4096)
            assert msg == 'TEST-MSG'
            event.app().break_main_loop()
        def send_timeout(self, event):
            print('send_timeout')
            self.sockpair[1].send('TEST-MSG')
            
    pair = socket.socketpair()
    app = SocketPairApp(pair)
    app.add_channel(pair[0], app.COND_READ, app.read_socket)
    app.add_timeout(500, app.send_timeout)
    app.main_loop()


#if __name__ == '__main__':
#    test_repeating_timeout()
#    test_cancel_timeout()
#    test_socket_channel()
