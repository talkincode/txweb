#!/usr/bin/env python
#coding:utf-8

from txweb.web import BaseHandler
from txweb.permit import permit

@permit.route("/hello")
class HelloHandler(BaseHandler):

    def get(self):
        self.write("hello")