import ntptime
import time

TRACE =False


def getdate(UTC_OFFSET):
    offset = UTC_OFFSET * 60 * 60 
    ntptime.settime()
    return time.localtime(time.time() + offset)

def trace(trace_message):
    if TRACE:
        print(trace_message);