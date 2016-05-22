#!/usr/bin/env python
#coding:utf-8

from txweb.web import BaseHandler
from txweb.permit import permit

@permit.route("/")
class IndexHandler(BaseHandler):

    def get(self):
        self.write("hello world")