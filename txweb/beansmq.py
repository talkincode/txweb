#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.internet import reactor, protocol, defer
from beanstalk.twisted_client import Beanstalk
from txweb import logger

"""
基于beanstalkd 封装的消息客户端。
"""

class BeansMq(object):

    def __init__(self,cli):
        self.cli = cli
        self.lock = defer.DeferredLock()

    def put(self,jobdata,tube=None,**kwargs):
        if not tube:
            return self.cli.put(jobdata,**kwargs)

        def _put(lock):
            try:
                self.cli.use(tube)
                return self.cli.put(jobdata,**kwargs)
            finally:
                lock.release()
        return self.lock.acquire().addCallbacks(_put,logger.error) 

    def reserve(self,tube=None,timeout=None):
        if not tube:
            return self.cli.reserve() if not timeout else self.cli.reserve_with_timeout(timeout)

        def _reserve(lock):
            try:
                self.cli.watch(tube)
                return self.cli.reserve() if not timeout else self.cli.reserve_with_timeout(timeout)
            finally:
                lock.release()
        return self.lock.acquire().addCallbacks(_reserve,logger.error) 

    def delete(self,jobid):
        return self.cli.delete(jobid)

    def release(self,jobid,**kwargs):
        return self.cli.release(jobid,**kwargs)

    def bury(self,jobid,**kwargs):
        return self.cli.bury(jobid,**kwargs)

    def watch(self,tube):
        return self.cli.watch(tube)

    def ignore(self,tube):
        return self.cli.ignore(tube)


@defer.inlineCallbacks
def setup(host,port):
    client = yield protocol.ClientCreator(reactor,Beanstalk).connectTCP(host,port)
    logger.info("beanstalkd connected")
    defer.returnValue(BeansMq(client))

