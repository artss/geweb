Geweb is an asyncronous python/gevent web framework.

Installation
------------

    pip install hg+https://bitbucket.org/arts/geweb

Create project
--------------

    geweb init myproject

Run server
----------

    cd myproject
    geweb run

App structure
-------------

    |- myproject
        |- myapp
            |- templates/
                |- tmpl1.html
                |- tmpl2.html
                |- ...
            |- __init__.py
            |- urls.py
