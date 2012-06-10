from apps.foo import foo

urls = [
    (r'^/foo$', foo),
    (r'^/foo/(?P<id>\d+)', foo),
]
