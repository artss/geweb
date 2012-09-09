import sys
import time
from hashlib import sha1
from datetime import datetime
from random import randint
from geweb.session import Session
from geweb.exceptions import Forbidden
from geweb.env import env

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

#CSRF decorator
def csrf(fn):
    def _fn(*args, **kwargs):
        if env.request.method == 'GET':
            csrf_token()
        else:
            sess = Session()
            token = env.request.args('csrf_token')
            sess_token = sess['csrf_token']
            del sess['csrf_token']
            sess.save()
            if not token or sess_token != token:
                raise Forbidden
        return fn(*args, **kwargs)
    return _fn

def csrf_token():
    sess = Session()
    token = sess['csrf_token']
    if token:
        return token
    token = sha1('%s%s%s' % (
        datetime.now(),
        randint(1000000, 9999999),
        env.request.path
    )).hexdigest()
    sess['csrf_token'] = token
    sess.save()
    return token

