import sys
import time

class Singleton(object):
    def __new__(cls, *args, **kwargs):
        name = "_%s__instance" % cls.__name__
        try:
            result = getattr(cls, name)
        except AttributeError:
            result = (super(Singleton, cls).__new__(cls, *args, **kwargs))
            setattr(cls, name, result)
        return result

    @classmethod
    def get_instance(cls):
        name = "_%s__instance" % cls.__name__
        return getattr(cls, name)

def uniqify(array):
    #return dict.fromkeys(array).keys()
    array_out = []
    for a in array:
        if a not in array_out:
            array_out.append(a)
    return array_out

def parse_email(address):
    m = re.match(r'^(?P<user>\w|\w[\w.-]*\w)@(?P<domain>(?:(?:\w|\w[\w-]*\w)\.)+(?:\w|\w[\w-]*\w))$', address)
    try:
        return m.groupdict()
    except AttributeError:
        return None

def timestamp(d):
    return time.mktime(d.timetuple())

def die(message):
    sys.stderr.write("%s\n" % message)
    sys.exit(1)

