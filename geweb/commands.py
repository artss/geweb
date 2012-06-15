import os
from geweb.util import die

def init(args):
    import shutil

    project_dir = os.path.abspath(os.path.join(os.getcwd(), args.project_name))

    settings_path = os.path.join(project_dir, 'settings.py')

    if os.path.exists(project_dir) and os.path.isdir(project_dir) \
            and os.path.exists(settings_path):
        die('Project is already initialized in %s' % project_dir)

    if os.path.exists(project_dir) and not os.path.isdir(project_dir):
        die('%s is not a directory')

    if not os.path.exists(project_dir):
        os.mkdir(project_dir)

    geweb_dir = os.path.dirname(__file__)
    data_dir = os.path.join(geweb_dir, 'data')

    settings_src = os.path.join(data_dir, 'settings.py.sample')
    if not os.path.exists(settings_src):
        die('Cannot open settings sample. Probably geweb is breken.')

    try:
        shutil.copy(settings_src, settings_path)
    except IOError:
        die('Cannot create settings.py')

    try:
        os.mkdir(os.path.exists(project_dir, 'templates'))
    except (IOError, OSError):
        die('Cannot create templates directory')

    print ''
    print 'Project is created. Now you may go to the project directory and run'
    print '  geweb run'
    print ''

def run(args):
    try:
        import settings
    except ImportError:
        die('Cannot import settings.py in %r.' % os.getcwd())

    if args.level and args.level not in ['error', 'warn', 'info', 'debug']:
        die('Invalid log level: %s' % args.level)

    if args.listen:
        addr = args.listen.rsplit(':', 1)
        if len(addr) == 2:
            host = addr[0]
            try:
                port = int(addr[1])
            except ValueError:
                die('Invalid address: %s' % args.listen)
        else:
            try:
                host = None
                port = int(args.listen)
            except ValueError:
                host = args.listen
                port = None
    else:
        host, port = None, None

    from geweb.server import run_server
    run_server(host, port, args.workers, args.debug,
               args.log, args.stdout, args.level)

