#!/usr/bin/env python
# coding=utf-8
import os
import types
import importlib
from twisted.internet.threads import deferToThread
from twisted.python import reflect
from twisted.internet import defer
from twisted.python import log

class EventDispatcher:

    def __init__(self, prefix="event_"):
        self.prefix = prefix
        self.callbacks = {}


    def sub(self, name, func,multi=True):
        if not multi:
            self.callbacks[name] = [func]
        else:
            self.callbacks.setdefault(name, []).append(func)
        log.msg('register event %s %s' % (name,(func.__doc__ or '')))

    def register(self, obj, multi=True):
        d = {}
        reflect.accumulateMethods(obj, d, self.prefix)
        for k,v in d.items():
            self.sub(k, v)

    def pub(self, name, *args, **kwargs):
        if name not in self.callbacks:
            return
        async = kwargs.pop("async",False)
        results = []
        for func in self.callbacks[name]:
            if async:
                deferd = deferToThread(func, *args, **kwargs)
                deferd.addCallbacks(lambda r:r,lambda e:e)
                results.append(deferd)
            else:
                result = func(*args, **kwargs)
                results.append(result)
        if async:
            return defer.DeferredList(results)
        else:
            return results


dispatch = EventDispatcher()
sub = dispatch.sub
pub = dispatch.pub
register = dispatch.register





