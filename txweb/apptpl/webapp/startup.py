#!/usr/bin/env python
#coding:utf-8
import os,sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__),os.path.pardir))
from txweb.dbutils import get_engine
from txweb.redis_cache import CacheManager
from txweb.dbutils import DBBackup
from txweb import redis_session as session
from txweb import logger,dispatch,utils
from txweb.permit import permit, load_handlers, load_events
from txweb.redis_conf import redis_conf
from txweb import utils
from sqlalchemy.orm import scoped_session, sessionmaker


def init(gdata):
    """    
    # gdata.db_engine = get_engine(gdata.config)
    # gdata.db = scoped_session(sessionmaker(bind=gdata.db_engine, autocommit=False, autoflush=False))

    # gdata.settings = dict(
    #     cookie_secret="12oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    #     login_url="/admin/login",
    #     template_path=os.path.join(os.path.dirname(__file__), "webapp/views"),
    #     static_path=os.path.join(os.path.dirname(__file__), "webapp/static"),
    #     xsrf_cookies=True,
    #     xheaders=True,
    # )

    # gdata.redisconf = redis_conf(gdata.config)
    # gdata.session_manager = session.SessionManager(gdata.redisconf,gdata.settings["cookie_secret"], 600)
    # gdata.cache = CacheManager(gdata.redisconf,cache_name='Cache-%s'%os.getpid())
    # gdata.cache.print_hit_stat(60)
    # gdata.db_backup = DBBackup(models.get_metadata(gdata.db_engine), excludes=[])
    # gdata.aes = utils.AESCipher(key=gdata.config.system.secret)

    # cache event init
    # dispatch.register(gdata.cache)
    """

    appname = os.path.basename(gdata.app_dir)
    utils.update_timezone(gdata.config.system.tz)
    syslog = logger.Logger(gdata.config,appname)
    dispatch.register(syslog)
    log.startLoggingWithObserver(syslog.emit, setStdout=0)

    # app handles init 
    handler_dir = os.path.join(gdata.app_dir,'handlers')
    load_handlers(handler_path=handler_dir,pkg_prefix="%s.handlers"%appname, excludes=[])
    gdata.all_handlers = permit.all_handlers

    # app event init
    event_dir = os.path.abspath(os.path.join(gdata.app_dir,'events'))
    load_events(event_dir,"%s.events"%appname,gdata=gdata)



