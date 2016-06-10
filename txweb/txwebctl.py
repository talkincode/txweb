
from txweb import choosereactor
choosereactor.install_optimal_reactor(False)
from txweb import web
from txweb import logger
from txweb import permit
from txweb.storage import Storage
from txweb.config import find_config
from txweb.permit import load_handlers
from cyclone.options import options,define,parse_command_line
from twisted.internet import reactor
from twisted.internet import defer
import sys,os
import importlib
import signal
import zipfile
import shutil

'''
simple :  txwebctl --dir=simple
'''

define("port", 0, type=int, help="application listen http port")
define("dir", '.',help="application dir")
define("conf", 'txweb.json',help="json config file ")
define('debug', type=bool, default=True)
define("create", type=bool, help="create application", default=False)
define("U", type=bool,help="create application with upgrade txweb template", default=False)

def create():
    import requests
    if os.path.exists(options.dir):
        if (raw_input('app dir %s is exists, delete it?[y/n]' % options.dir) or 'n') is 'n':
            return 
        if options.dir in ("/","/usr",'/var','/opt','dev','/boot','/etc','/home','sbin','/srv','/root','/lib','/lib64'):
            print 'oh! you are bad egg!'
            return
        shutil.rmtree(options.dir)

    appname = os.path.basename(options.dir)
    appdir = os.path.abspath(options.dir) 
    if not os.path.exists("/tmp/txweb-template.zip") or options.U:
        r = requests.get('https://github.com/talkincode/txweb-template/archive/master.zip')
        with open("/tmp/txweb-template.zip",'w') as rf:
            rf.write(r.content)
    zipFile = zipfile.ZipFile("/tmp/txweb-template.zip")
    zipFile.extractall('/tmp/txweb-template')
    shutil.move("/tmp/txweb-template/txweb-template-master", appdir)
    shutil.move(os.path.join(appdir,'txwebproject'), os.path.join(appdir,appname))
    shutil.move(os.path.join(appdir,'etc/txwebproject'), os.path.join(appdir,'etc/%s'%appname))
    shutil.move(os.path.join(appdir,'etc/txwebproject.json'), os.path.join(appdir,'etc/%s.json'%appname))
    shutil.move(os.path.join(appdir,'etc/txwebproject.conf'), os.path.join(appdir,'etc/%s.conf'%appname))
    shutil.move(os.path.join(appdir,'etc/txwebproject.service'), os.path.join(appdir,'etc/%s.service'%appname))
    for root, dirs, files in os.walk(appdir):
        for fpath in files:
            fpath = os.path.join(root,fpath)
            print 'update file %s'%fpath
            if os.path.isfile(fpath):
                rf = open(fpath)
                ft2 = rf.read()
                rf.close()
                with open(fpath,'wb') as wf:
                    wf.write(ft2.replace('{txwebproject}',appname))

    print 'create application %s done' % appname

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
    initd = startup.init(gdata)

    def initapp(r):
        app = web.Application(gdata)
        reactor.listenTCP(gdata.port or int(gdata.config.web.port), app, interface=gdata.config.web.host)

    def initerr(err):
        logger.exception(err)
        reactor.stop()

    if isinstance(initd, defer.Deferred):
        initd.addCallbacks(initapp,initerr)
    else:
        initapp(gdata)


    def exit_handler(signum, stackframe): 
        reactor.callFromThread(reactor.stop)
    signal.signal(signal.SIGTERM, exit_handler)
    reactor.run()


