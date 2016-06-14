#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.internet import reactor, protocol, defer
from beanstalk.twisted_client import Beanstalk
from txweb import logger

"""
基于beanstalkd 封装的消息客户端。
"""

class BeansMq(object):

    def __init__(self,cli,tube=None):
        self.cli = cli
        if tube:
            self.cli.watch(tube)

    def put(self,jobdata,**kwargs):
        return self.cli.put(jobdata,**kwargs)

    def reserve(self,timeout=None):
        return self.cli.reserve() if not timeout else self.cli.reserve_with_timeout(timeout)

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
def setup(host,port,tube=None):
    client = yield protocol.ClientCreator(reactor,Beanstalk).connectTCP(host,port)
    logger.info("beanstalkd connected")
    defer.returnValue(BeansMq(client,tube=tube))

