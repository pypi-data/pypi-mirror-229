import inspect
import os


def get_location(depth=0):
    frame = inspect.currentframe().f_back
    return (
        os.path.basename(frame.f_code.co_filename),
        frame.f_code.co_name,
        frame.f_lineno,
    )
