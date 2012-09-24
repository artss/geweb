from jinja2 import environmentfilter

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

filters = {
    'strftime': strftime
}
