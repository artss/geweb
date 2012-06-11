from jinja2 import environmentfilter

@environmentfilter
def strftime(env, time, format):
    return time.strftime(format)

filters = {
    'strftime': strftime
}
