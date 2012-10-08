from jinja2 import environmentfilter
import urllib

@environmentfilter
def strftime(env, time, format):
    """
    Datetime format filter.
    
    Usage:
    {{ dt|strftime("%Y-%m-%d %H:%M:%s") }}
    """
    if not time:
        return ''
    return time.strftime(format)

@environmentfilter
def urlencode(env, s):
    return urllib.quote_plus(s.encode('utf-8'))

filters = {
    'strftime': strftime,
    'urlencode': urlencode,
}
