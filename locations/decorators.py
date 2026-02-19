
import time
import datetime
from functools import wraps

def convert_seconds_to_hmsm(total_seconds):
    duration = datetime.timedelta(seconds=total_seconds)
    total_milliseconds = int(duration.total_seconds() * 1000)
    hours, remainder = divmod(total_milliseconds, 3600000) # 1 hour = 3,600,000 ms
    minutes, remainder = divmod(remainder, 60000) # 1 minute = 60,000 ms
    seconds, milliseconds = divmod(remainder, 1000) # 1 second = 1,000 ms
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

def time_of_execution(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time (H:M:S.mmm) of {func.__name__}: {convert_seconds_to_hmsm(execution_time)}")
        return result
    return wrapper