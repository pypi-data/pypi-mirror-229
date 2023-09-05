import os
import time
import traceback, sys

from stderrstdoutcapture import GetStdErr
from touchtouch import touch


def get_timestamp(sep="_"):
    return (kj := time.time()), (
        time.strftime(f"%Y{sep}%m{sep}%d{sep}%H{sep}%M{sep}%S")
        + f"{sep}"
        + (str(kj).split(".")[-1] + "0" * 10)[:6]
    )


def pfehler(logfile=None, print_error=True):
    r"""
    Capture and log exceptions, optionally printing them to stderr.
    
    Args:
        logfile (str, optional): The path to the error log file where the exception details
            will be appended. If not provided, no logging to a file will occur.
        print_error (bool, optional): If True, the exception details will be printed to stderr.
            If False, no output will be printed. Defaults to True.
    
    Example:
        from pfehler import pfehler
        try:
            x = 5 / 0
        except Exception:
            pfehler(logfile="c:\\errorlogfile.txt", print_error=True)
    
    This function captures an exception's traceback, optionally prints it to stderr, and
    appends the error details along with a timestamp to a specified log file. If the log file
    does not exist, it will be created. The timestamp format is "YYYY_MM_DD_HH_MM_SS_microseconds".
    
    """
    etype, value, tb = sys.exc_info()
    with GetStdErr() as o:
        traceback.print_exception(etype, value, tb)
    if print_error:
        for line in o:
            sys.stderr.write(line.strip())
    if logfile:
        if not os.path.exists(logfile):
            touch(logfile)
        with open(logfile, "a") as f:
            tstamp = get_timestamp()
            f.write(tstamp[1])
            f.write(f"\n{'-'*len(tstamp[1])}\n")
            f.write(o[0].strip())
            f.write("\n__________________________________________________________\n")


