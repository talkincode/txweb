#!/usr/bin/env python
#coding:utf-8
import os
from txweb.dbutils import get_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from txweb.redis_cache import CacheManager
from txweb.dbutils import DBBackup
from txweb import redis_session as session
from txweb import logger
from txweb import dispatch
from txweb import utils
from txweb.permit import permit, load_handlers, load_events
from twisted.python import log

def redis_conf(config):
    eredis_url = os.environ.get("REDIS_URL")
    eredis_port = os.environ.get("REDIS_PORT")
    eredis_pwd = os.environ.get("REDIS_PWD")
    eredis_db = os.environ.get("REDIS_DB")

    is_update = any([eredis_url,eredis_port,eredis_pwd,eredis_db])

    if eredis_url:
        config['redis']['host'] = eredis_url
    if eredis_port:
        config['redis']['port'] = int(eredis_port)
    if eredis_pwd:
        config['redis']['passwd'] = eredis_pwd 
    if eredis_db:
        config['redis']['db'] = int(eredis_db)
    if is_update:
        config.save()

    return config['redis']

def update_timezone(config):
    if 'TZ' not in os.environ:
        os.environ["TZ"] = config.system.tz
    try:time.tzset()
    except:pass

def init(gdata):
    update_timezone(gdata.config)
    syslog = logger.Logger(gdata.config,'txweb')
    dispatch.register(syslog)
    log.startLoggingWithObserver(syslog.emit, setStdout=0)

    gdata.db_engine = get_engine(gdata.config)
    gdata.db = scoped_session(sessionmaker(bind=gdata.db_engine, autocommit=False, autoflush=False))

    gdata.settings = dict(
        cookie_secret="12oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
        login_url="/admin/login",
        template_path=os.path.join(os.path.dirname(__file__), "webapp/views"),
        static_path=os.path.join(os.path.dirname(__file__), "webapp/static"),
        xsrf_cookies=True,
        xheaders=True,
    )

    gdata.redisconf = redis_conf(gdata.config)
    gdata.session_manager = session.SessionManager(gdata.redisconf,gdata.settings["cookie_secret"], 600)
    gdata.cache = CacheManager(gdata.redisconf,cache_name='Cache-%s'%os.getpid())
    gdata.cache.print_hit_stat(60)
    # gdata.db_backup = DBBackup(models.get_metadata(gdata.db_engine), excludes=[])
    gdata.aes = utils.AESCipher(key=gdata.config.system.secret)

    # cache event init
    dispatch.register(gdata.cache)

    # app handles init 
    handler_dir = os.path.join(gdata.app_dir,'webapp/handlers')
    load_handlers(handler_path=handler_dir,pkg_prefix="demo.webapp.handlers", excludes=[])
    gdata.all_handlers = permit.all_handlers

    # app event init
    event_dir = os.path.abspath(os.path.join(gdata.app_dir,'webapp/events'))
    if os.path.exists(event_dir):
        load_events(event_dir,"demo.webapp.events",gdata=gdata)



