Geweb is an asyncronous micro web framework based on gevent.

Installation
------------

    pip install geweb

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
