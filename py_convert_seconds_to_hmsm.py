import datetime

def convert_seconds_to_hmsm(total_seconds):
    # Timedelta stores time internally in days, seconds, and microseconds.
    # It automatically handles fractional seconds.
    duration = datetime.timedelta(seconds=total_seconds)

    # Format the duration string. The default string representation 
    # includes days if applicable (e.g., '1 day, 0:11:06').

    # For a custom hh:mm:ss.mmm format (handling potential days by keeping total hours):
    total_milliseconds = int(duration.total_seconds() * 1000)
    hours, remainder = divmod(total_milliseconds, 3600000) # 1 hour = 3,600,000 ms
    minutes, remainder = divmod(remainder, 60000) # 1 minute = 60,000 ms
    seconds, milliseconds = divmod(remainder, 1000) # 1 second = 1,000 ms
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

# Example usage:



#! To Run: python py_convert_seconds_to_hmsm.py

if __name__ == "__main__":
    seconds_input = 12345.6789
    formatted_time = convert_seconds_to_hmsm(seconds_input)
    print(f"Time in H:M:S.mmm format: {formatted_time}")

    seconds_input_long = 1234567.8910
    formatted_time_long = convert_seconds_to_hmsm(seconds_input_long)
    print(f"Time in H:M:S.mmm format (long): {formatted_time_long}")
