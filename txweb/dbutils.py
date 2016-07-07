#!/usr/bin/env python
#coding:utf-8
import os
import functools
import json
import json
import gzip
try:
    from sqlalchemy import *
except:
    pass

ISOLATION_LEVEL = {
    1 : 'READ COMMITTED',
    2 : 'READ UNCOMMITTED',
    3 : 'REPEATABLE READ',
    4 : 'SERIALIZABLE'
}


class DBEngine(object):

    def __init__(self,config, **kwargs):
        self.config = config
        self.dbtype = os.environ.get("DB_TYPE", self.config.database.dbtype)
        self.dburl = os.environ.get("DB_URL", self.config.database.dburl)
        self.dbinit = os.environ.get("DB_INIT", 1)
        self.pool_size = kwargs.pop('POOL_SIZE',self.config.database.pool_size)

    def __call__(self):
        return self.get_engine()

    def get_engine(self):
        if self.dbtype == 'mysql':
            return create_engine(
                self.dburl,
                echo=bool(self.config.database.echo),
                pool_size = int(self.pool_size),
                pool_recycle=int(self.config.database.pool_recycle)
            )
        elif self.dbtype == 'postgresql':
            return create_engine(
                self.dburl,
                echo=bool(self.config.database.echo),
                pool_size = int(self.pool_size),
                isolation_level = int(ISOLATION_LEVEL.get(self.config.database.isolation_level, 'READ COMMITTED')),
                pool_recycle=int(self.config.database.pool_recycle)
            )
        elif self.dbtype == 'sqlite':
            def my_con_func():
                import sqlite3.dbapi2 as sqlite
                con = sqlite.connect(self.dburl.replace('sqlite:///',''))
                con.text_factory=str
                # con.execute("PRAGMA synchronous=OFF;")
                # con.isolation_level = 'IMMEDIATE'
                return con
            return create_engine(
                "sqlite+pysqlite:///",
                creator=my_con_func,
                echo=bool(self.config.database.echo)
            )
        else:
            return create_engine(
                self.dburl,
                echo=bool(self.config.database.echo),
                pool_size = int(self.pool_size)
            )

class DBBackup:

    def __init__(self, sqla_metadata, excludes=[]):
        self.metadata = sqla_metadata
        self.excludes = excludes
        self.dbengine = self.metadata.bind

    def dumpdb(self, dumpfile):
        _dir = os.path.split(dumpfile)[0]
        if not os.path.exists(_dir):
            os.makedirs(_dir)

        with self.dbengine.begin() as db:
            with gzip.open(dumpfile, 'wb') as dumpfs:
                tables = {_name:_table for _name, _table in self.metadata.tables.items() if _name not in self.excludes}
                table_headers = ('table_names', tables.keys())
                dumpfs.write(json.dumps(table_headers, ensure_ascii=False).encode('utf-8'))
                dumpfs.write('\n')
                for _name,_table in tables.iteritems():
                    rows = db.execute(select([_table]))
                    for row in rows:
                        obj = (_name, dict(row.items()))
                        dumpfs.write(json.dumps(obj,ensure_ascii=False).encode('utf-8'))
                        dumpfs.write('\n')



    def restoredb(self,restorefs,batch_num=49):
        if not os.path.exists(restorefs):
            print 'backup file not exists'
            return
        
        with self.dbengine.begin() as db:
            with gzip.open(restorefs,'rb') as rfs:
                cache_datas = {}
                for line in rfs:
                    try:
                        tabname, rdata = json.loads(line)
                        if tabname == 'table_names' and rdata:
                            for table_name in rdata:
                                print "clean table %s" % table_name
                                db.execute("delete from %s;" % table_name)
                            continue

                        if tabname not in cache_datas:
                            cache_datas[tabname] = [rdata]
                        else:
                            cache_datas[tabname].append(rdata)

                        if tabname in cache_datas and len(cache_datas[tabname]) >= batch_num:
                            print 'insert datas<%s> into %s' % (len(cache_datas[tabname]), tabname)
                            db.execute(self.metadata.tables[tabname].insert().values(cache_datas[tabname]))
                            del cache_datas[tabname]

                    except:
                        print 'error data %s ...'% line
                        raise

                print "insert last data"
                for tname, tdata in cache_datas.iteritems():
                    try:
                        print 'insert datas<%s> into %s' % (len(tdata), tname)
                        db.execute(self.metadata.tables[tname].insert().values(tdata))
                    except:
                        print 'error data %s ...' % tdata
                        raise

                cache_datas.clear()

def get_engine(config, pool_size=0):
    if pool_size > 0:
        return DBEngine(config,pool_size=pool_size)()
    else:
        return DBEngine(config)()

class make_db:
    def __init__(self, mkdb):
        self.conn = mkdb()

    def __enter__(self):
        return self.conn   

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.conn.close()

def serial_model(mdl):
    if not mdl:return
    if not hasattr(mdl,'__table__'):return
    data = {}
    for c in mdl.__table__.columns:
        data[c.name] = getattr(mdl, c.name)
    return json.dumps(data,ensure_ascii=False)


