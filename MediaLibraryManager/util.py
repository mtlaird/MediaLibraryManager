import datetime
from math import trunc


def convert_bytes_to_friendly_size(nbytes):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    i = 0
    while nbytes >= 1024 and i < len(suffixes) - 1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])


def convert_seconds_to_friendly_time(seconds, short=True):
    ret_string = ""
    days = trunc(seconds / 86400)
    hours = trunc((seconds % 86400) / 3600)
    minutes = trunc((seconds % 3600) / 60)
    rem_seconds = trunc(seconds % 60)
    if days > 0:
        ret_string += "{d}".format(d=days)
        if short:
            ret_string += "d"
        elif days == 1:
            ret_string += " day "
        else:
            ret_string += " days "
    if hours > 0:
        ret_string += "{h}".format(h=hours)
        if short:
            ret_string += "h"
        elif hours == 1:
            ret_string += " hour "
        else:
            ret_string += " hours "
    if minutes > 0:
        ret_string += "{m}".format(m=minutes)
        if short:
            ret_string += "m"
        elif minutes == 1:
            ret_string += " minute "
        else:
            ret_string += " minutes "
    if rem_seconds > 0:
        ret_string += "{s}".format(s=rem_seconds)
        if short:
            ret_string += "s"
        elif rem_seconds == 1:
            ret_string += " second"
        else:
            ret_string += " seconds"
    return ret_string


def convert_epoch_to_friendly_date(epoch):
    return datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')
