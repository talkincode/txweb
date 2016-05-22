
from txweb import choosereactor
choosereactor.install_optimal_reactor(False)
from txweb import web
from txweb import permit
from txweb.storage import Storage
from txweb.config import find_config
from txweb.permit import load_handlers
from cyclone.options import options,define,parse_command_line
from twisted.internet import reactor
import sys,os
import importlib
import signal

'''
simple :  txwebctl --dir=simple
'''

define("port", 0, type=int)
define("dir", '.')
define("conf", 'txweb.json')
define('debug', type=bool, default=True)
define("create", type=bool, default=False)

def create():
    if os.path.exists(options.dir):
        print 'app dir %s is exists' % options.dir
        return 
    import shutil
    appdir = os.path.abspath(options.dir) 
    tpldir =  os.path.join(os.path.dirname(__file__), "apptpl")
    shutil.copytree(tpldir, appdir)
    shutil.move(os.path.join(appdir,'webapp'), os.path.join(appdir,os.path.basename(appdir)))
    print 'create app done'

def main():
    parse_command_line()
    if options.create:
        return create()
    gdata = Storage()
    gdata.port = options.port
    gdata.debug = options.debug
    gdata.app_dir = os.path.abspath(options.dir)
    if not os.path.exists(options.dir):
        print 'app dir not exists'
        sys.exit(0)

    sys.path.insert(0, gdata.app_dir)

    if r'/' in options.conf:
        gdata.config_file = os.path.abspath(options.conf)
    else:
        gdata.config_file = os.path.abspath(os.path.join(options.dir,options.conf))

    gdata.config = find_config(gdata.config_file)

    startup = importlib.import_module('startup')
    startup.init(gdata)

    app = web.Application(gdata)
    reactor.listenTCP(gdata.port or int(gdata.config.web.port), app, interface=gdata.config.web.host)
    def exit_handler(signum, stackframe): 
        reactor.callFromThread(reactor.stop)
    signal.signal(signal.SIGTERM, exit_handler)
    reactor.run()


