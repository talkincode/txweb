#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.internet import reactor, protocol, defer
from beanstalk.twisted_client import Beanstalk
from txweb import logger

"""
基于beanstalkd 封装的消息客户端。
"""

class BeansMq(object):

    @defer.inlineCallbacks
    def __call__(self,host,port,tubes=[]):
        self.pools = {}
        for tube in tubes:
            client = yield protocol.ClientCreator(reactor,Beanstalk).connectTCP(host,port)
            client.watch(tube)
            self.pools[tube] = client
        defer.returnValue(self)

    def put(self,tube, jobdata,**kwargs):
        if tube in self.pools:
            return self.pools[tube].put(jobdata,**kwargs)

    def reserve(self,tube,timeout=None):
        if tube in self.pools:
            client = self.pools[tube]
            return client.reserve() if not timeout else client.reserve_with_timeout(timeout)

    def delete(self,tube,jobid):
        if tube in self.pools:
            return self.pools[tube].delete(jobid)

    def release(self,tube,jobid,**kwargs):
        if tube in self.pools:
            return self.pools[tube].release(jobid,**kwargs)

    def bury(self,tube,jobid,**kwargs):
        if tube in self.pools:
            return self.pools[tube].bury(jobid,**kwargs)


BMQ = BeansMq()
