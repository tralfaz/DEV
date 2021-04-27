import select

class EventInputEntry(object):

  def __init__(self, inputId, condition, callback, clientData):

class EventApp(object):

  INPUT_READ_MASK  = 0x01
  INPUT_WRITE_MASK = 0x02
  INPUT_ERROR_MASK = 0x04

  def __init__(self):
    self._inputID         = 0
    self._inputHandlers   = {}
    self._timeoutID       = 0
    self._timeoutHandlers = {}

  def addInput(self, source, conditions, callback, clientData):
    """
    Arguments:
      source, File like object to monitor for specified conditions.
      conditions, Bitmask of INPUT_*_MASK conditions states
      callback, Callable to be invoked when input condition occurs
      clientData, Arbitrary value to pass to callback
    Returns:
      InputID, unique numeric identifier of input registration.
    """
    
    return inputId

#  def addSignal(self, signalNum, callback, clientData):
#  def addWorkProc(self, callback, clientData):

  def addTimeout(self, interval, callback, clientData):
    """
    Arguments:
      interval, Time till invocation in milli-seconds
      callback, Callable to be invoked when interval has elapsed.
      clientData, Arbitrary value to pass to callback
    Returns:
      TimeoutID, unique numeric identifier of timeout registration.
    """

  def dispatchEvent(self, event):

  def mainLoop(self):
    while True:
      event = self.nextEvent()
      self.dispatchEvent(event)
      if self._mainLoopExit:
        break

  def nextEvent(self):

  def processEvent(self, evenTypes):

eventTypes;
mask	Specifies what types of events to process. The mask is the bitwise inclusive OR of any combination of XtIMXEvent, XtIMTimer, XtIMAlternateInput, and XtIMSignal. As a convenience, Intrinsic.h defines the symbolic name XtIMAll to be the bitwise inclusive OR of these four event types.
The XtAppProcessEvent function processes one timer, input source, signal source, or X event. If there is no event or input of the appropriate type to process, then XtAppProcessEvent blocks until there is. If there is more than one type of input available to process, it is undefined which will get processed. Usually, this procedure is not called by client applications; see XtAppMainLoop. XtAppProcessEvent processes timer events by calling any appropriate timer callbacks, input sources by calling any appropriate input callbacks, signal source by calling any appropriate signal callbacks, and X events by calling XtDispatchEvent.

When an X event is received, it is passed to XtDispatchEvent, which calls the appropriate event handlers and passes them the widget, the event, and client-specific data registered with each procedure. If no handlers for that event are registered, the event is ignored and the dispatcher simply returns.

  def removeInput(self, inputId):
    self._inputHandlers.pop(inputId, None)

  def removeTimeout(self, timeoutId):
    self._timeoutHandlers.pop(timeoutId, None)


  def _selectInvent(self):
    
    rset, wset, xset = select.select(rTest, wTest, xTest, wait)
fdev060401> 
