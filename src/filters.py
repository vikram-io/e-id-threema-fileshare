import datetime

def datetime_filter(timestamp):
    """Convert a timestamp to a formatted date string"""
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
