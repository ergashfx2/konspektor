import re

def validate_time_format(time_string: str):
    time_pattern = r"^(?:[01]?\d|2[0-3]):([0-5]?\d)$"

    if re.match(time_pattern, time_string):
        return True
    else:
        return False