"""
Classes associated with the EventsApp base class used for creating
applications that process multiple timer and file based input sources.
"""

import os
import select
import struct
import time


class EventChannelEntry(object):
    """Event entry for monitoring a single file based channel for either
    input or output readiness."""

    def __init__(self, app, eid, chan_obj, conditions, callback, userdata):
        """Creates an EventChannel entry to invoke the supplied callback
        whenever the supplied channel file objects I/O condition matches
        one of condition bits set in the conditions bit mask.
        Arguments:
          app,        Reference to EventsApp instance that created this entry
          eid,        The entry Id uniquely identifies this entry instance
          chan_obj,   Channel file object to be monitored
          conditions, Bit masks of EventsApp.COND_xxx that invoke callback
          callback,   Function to call when I/O condition met
          userdata,   Arbitrary user data to associate with this entry
        """
        self._app        = app
        self._eid        = eid
        self._chan_obj   = chan_obj
        self._cond_mask  = conditions
        self._cond_event = 0
        self._callback   = callback
        self._userdata   = userdata

    def app(self):
        """Return a reference to the EventsApp that created this entry."""
        return self._app

    def channel(self):
        """Return the channel file object for this entry"""
        return self._chan_obj

    def conditions_mask(self):
        """Return the condition bitmask that this entry respond to."""
        return self._cond_mask

    def event_conditions(self):
        """Return the channels conditions bitmask that trigger the callback."""
        return self._cond_event

    def eid(self):
        """Return the timeout entry id, used to cancel the timeout."""
        return self._eid

    def userdata(self):
        """Return the user data bound to the entry."""
        return self._userdata

    def _invoke_poll_event(self):
        """Invoke callback specified for this entry providing a reference
        to this entry as the sole argument to the callback."""
        self._callback(self)



class EventTimeoutEntry(object):
    """Event entry for a single timeout entry that inokes a callback when
    th specified number milli-seconds have elapsed."""

    def __init__(self, app, eid, duration, callback, userdata, repeat=False):
        """Creates an EventTimeout entry to invoke the supplied callback
        whenever the specified timeout period expires.  Unless repeat is
        set to True the entry wil remove itself after invoking the timeout
        callback.
        Arguments:
          app,      Reference to EventsApp instance that created this entry
          eid,      The entry Id uniquely identifies this entry instance
          duration, Number of milli-seconds until callback should fire
          callback, Function to call when timeout duration elapses
          userdata, Arbitrary user data to associate with this entry
          repeat,   If True the invoke callback every duration period
        """
        self._app      = app
        self._eid      = eid
        self._duration = duration
        self._callback = callback
        self._userdata = userdata
        self._repeat   = repeat
        self._epoch    = long(time.time() * 1000)
        self._ttl      = long(duration)

    def app(self):
        """Return a reference to the EventsApp that created this entry."""
        return self._app

    def duration(self):
        """Return timeout duration in milli-seconds specified at creation."""
        return self._duration

    def eid(self):
        """Return the timeout entry id, used to cancel the timeout."""
        return self._eid

    def repeats(self):
        """Return True if this timeout is a repeating timeout."""
        return self._repeat

    def userdata(self):
        """Return the user data bound to the entry."""
        return self._userdata

    def _invoke_timeout(self):
        """Invoke the callback for this timeout entry."""
        self._callback(self)

    def _update_ttl(self, now):
        """Update this timeut entries time-to-live(ttl) value based on the
        supplied now time in milli-seconds.
        Arguments:
          now, Current time in milli-seconds
        Return:
          The timeout entries new ttl value
        """
        self._ttl = long(self._duration - (now - self._epoch))
        return self._ttl



class EventsApp(object):
    """Base class for event based applicaion.  This can be used unaltered,
    or sub-classed for a specific event based application implementation."""

    COND_ERROR    = select.POLLERR
    COND_PRIORITY = select.POLLPRI
    COND_READ     = select.POLLIN
    COND_WRITE    = select.POLLOUT

    _POLL_CTRL_FMT = '=cI'
    _POLL_CTRL_LEN = struct.calcsize(_POLL_CTRL_FMT)

    def __init__(self):
        """Create an EventsApp instance with no event entries.  At least
        event entry is expected to added prior to calling main_loop()."""
        self._channel_id = 1
        self._timeout_id = 1
        self._run_main_loop = False

        self._channels_by_id = {}
        self._channels_by_fd = {}
        self._timeouts_by_id = {}

        self._poller = select.poll()

        rdfd, wrfd = os.pipe()
        self._poll_ctl_read  = rdfd
        self._poll_ctl_writ  = wrfd
        self._poll_ctl_input = (rdfd, select.POLLIN)
        self.add_channel(self._poll_ctl_read, EventsApp.COND_READ,
                         self._control_pipe_input)

    def add_channel(self, channel, conditions, callback, userdata=None):
        """Add a file based channel to be monitored for the specific I/O
        conditions.  The same channel can be added for different, or even
        the same conditions.  The supplied callback will be invoked whenever
        the channels I/O state matches one of the bits set in the conditions
        bitmask.
        Arguments:
          channel,    Channel file object to be monitored
          conditions, Bit masks of EventsApp.COND_xxx that invoke callback
          callback,   Function to call when I/O condition met
          userdata,   Arbitrary user data to associate with this entry
        Returns:
          The unique event entry id, that can be used in remove_channel.
        """
        channel_id = self._timeout_id
        self._channel_id += 1

        entry = EventChannelEntry(self, channel_id,
                                  channel, conditions, callback, userdata)
        self._channels_by_id[channel_id] = entry
        chan_fd = channel if isinstance(channel,int) else channel.fileno()
        self._channels_by_fd.setdefault(chan_fd, []).append(entry)

        fd_entries = self._channels_by_fd.get(chan_fd)
        if len(fd_entries) == 1:
            self._poller.register(chan_fd, conditions)
        else:
            poll_mask = 0
            for entry in fd_entries:
                poll_mask |= entry._cond_mask
            self._poller.modify(chan_fd, poll_mask)

        return channel_id

    def add_timeout(self, timeout, callback, userdata=None, repeat=False):
        """Add a timeout entry to invoke supplied callback after the
        specified milli-second duration has elapsed.  By default the
        timeout is a single shot timeout unless repeat is set to True.
        Arguments:
          timeout,  Milli-seconds to wait before invoking callback
          callback, Function to call when I/O condition met
          userdata, Arbitrary user data to associate with this entry
          repeat,   If True invoke callback after each timeout period
        Returns:
          The unique event entry id, that can be used in remove_timeout
        """
        timeout_id = self._timeout_id
        self._timeout_id += 1

        entry = EventTimeoutEntry(self, timeout_id,
                                  timeout, callback, userdata, repeat)
        self._timeouts_by_id[timeout_id] = entry

        return timeout_id

    def break_main_loop(self):
        """Cause the main_loop() method to exit and return to the caller."""
        ctrl_msg = struct.pack(EventsApp._POLL_CTRL_FMT, 'X', 0)
        os.write(self._poll_ctl_writ, ctrl_msg)

    def main_loop(self):
        """Run application main event loop until program exits or the app
        requests the loop break with the break_main_loop() method."""
        poll_timeout = None
        self._run_main_loop = True
        while self._run_main_loop:

            if self._timeouts_by_id and poll_timeout is None:
                now = long(time.time() * 1000)
                poll_timeout = self._next_timeout(now)

            ready_chans = self._poller.poll(poll_timeout)
            if not ready_chans:
                # A timeout occured, fire past due timeout entries
                poll_timeout = self._fire_timeouts()

            else:
                poll_timeout = None
                self._fire_ready_channels(ready_chans)

    def remove_channel(self, channel_id):
        """Remove an channel event entry given entry id from the current set
        of monitored channels.  Note if multiple entries exist for the same
        channel file object only entry for supplied id will be removed.
        Arguments:
          channel_id, ID of channel event entry.
        Returns:
          True if entry removed, False otherwise
        """
        entry = self._channels_by_id.pop(channel_id, None)
        if not entry:
            return False

        chan_fd = entry.channel() if type(entry.channel()) is int \
                  else entry.channel().fileno()
        fd_entries = self._channels_by_fd.get(chan_fd, [])
        if entry in fd_entries:
            fd_entries.remove(entry)
            if len(fd_entries) == 0:
                self._poller.unregister(chan_fd)
            else:
                poll_mask = 0
                for fdent in fd_entries:
                    poll_mask |= fdent._cond_mask
                self._poller.modify(chan_fd, poll_mask)
            return True

        return False

    def remove_timeout(self, timeout_id):
        """Remove a timeout event entry with the given timeout id.
        Arguments:
          timeout_id, The timeout entry id returned from add_timeout()
        Returns:
          True if entry removed, False otherwise
        """
        entry = self._timeouts_by_id.pop(timeout_id, None)
        return entry is not None

    # Protected
    #
    def _control_pipe_input(self, entry):
        """Internal control pipe channel entry callback invoked whenever
        there is a cotrol message on the control pipe to be read.
        Process internal control messages a appropriate.
        Arguments:
          entry, The channel event entry for the control pipe
        """
        ctlbuf = os.read(self._poll_ctl_read, EventsApp._POLL_CTRL_LEN)
        ctlmsg = struct.unpack(EventsApp._POLL_CTRL_FMT, ctlbuf)
        if ctlmsg[0] == 'X':
            # Break main loop control message
            self._run_main_loop = False

    def _fire_ready_channels(self, ready_list):
        """Find channel event entries that match the ready descriptor and
        condition mask.  Invoke the entry callback for each matched entry.
        Arguments:
          ready_list, (fd,conditions) tuple list from poller
        """
        for chan_fd, chan_cond in ready_list:
            fd_entries = self._channels_by_fd.get(chan_fd,[])
            for entry in fd_entries:
                entry._cond_event = chan_cond & entry._cond_mask
                if entry._cond_event:
                    entry._callback(entry)

    def _fire_timeouts(self):
        """Find all timeout event entries that expired and invoke the
        callback each expired entry.  Also update the time-to-live(ttl)
        value for all entries.  Each expired non-repeating entry is
        removed from the timeout entry set.
        Returns:
          The updated poll timeout value for the next main loop iteration
        """
        now = long(time.time() * 1000)
        expired_timeouts = [entry
                            for entry in self._timeouts_by_id.itervalues()
                            if entry._update_ttl(now) <= 0]

        for entry in expired_timeouts:
            entry._invoke_timeout()
            if entry._repeat:
                entry._ttl = entry._duration
            else:
                self._timeouts_by_id.pop(entry._eid, None)

        return self._next_timeout()

    def _next_timeout(self, now=None):
        """Determine the next poll timeout value for the next main loop
        iteration.  If a new now value is supplied update all the TTL values
        for the timeout entries.
        Returns:
          The updated poll timeout value for the next main loop iteration
        """
        if len(self._timeouts_by_id) == 0:
            return None

        if now is None:
            next_to = min([entry._ttl
                           for entry in self._timeouts_by_id.itervalues()])
        else:
            next_to = min([entry._update_ttl(now)
                           for entry in self._timeouts_by_id.itervalues()])
        return int(next_to)
