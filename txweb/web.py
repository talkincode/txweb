#!/usr/bin/env python
#coding:utf-8
import json
import re
import urlparse
import urllib
import traceback
import cyclone.web
import tempfile
import functools
import urlparse
from urllib import urlencode
from txweb.paginator import Paginator
from txweb.apiutils import apistatus
from txweb import apiutils

class Application(cyclone.web.Application):

    def __init__(self, gdata):
        self.config = gdata.config
        self.gdata = gdata
        cyclone.web.Application.__init__(self, gdata.all_handlers, **gdata.get('settings',{}))

class BaseHandler(cyclone.web.RequestHandler):
    
    def __init__(self, *argc, **argkw):
        super(BaseHandler, self).__init__(*argc, **argkw)
        self.gdata = self.application.gdata
        
    def check_xsrf_cookie(self):
        if self.gdata.config.system.get('production',False):
            return super(BaseHandler, self).check_xsrf_cookie()

    def initialize(self):
        pass
        
    def on_finish(self):
        pass
        

    def get_page_data(self, query):
        page_size = self.application.settings.get("page_size",15)
        page = int(self.get_argument("page", 1))
        offset = (page - 1) * page_size
        result = query.limit(page_size).offset(offset)
        page_data = Paginator(self.get_page_url, page, query.count(), page_size)
        page_data.result = result
        return page_data
   

    def get_page_url(self, page, form_id=None):
        if form_id:
            return "javascript:goto_page('%s',%s);" %(form_id.strip(),page)
        path = self.request.path
        query = self.request.query
        qdict = urlparse.parse_qs(query)
        for k, v in qdict.items():
            if isinstance(v, list):
                qdict[k] = v and v[0] or ''

        qdict['page'] = page
        return path + '?' + urllib.urlencode(qdict)

        
    def get_params(self):
        arguments = self.request.arguments
        params = {}
        for k, v in arguments.items():
            if len(v) == 1:
                params[k] = v[0]
            else:
                params[k] = v
        return params

    def get_params_obj(self, obj):
        arguments = self.request.arguments
        for k, v in arguments.items():
            if len(v) == 1:
                if type(v[0]) == str:
                    setattr(obj, k, v[0].decode('utf-8', ''))
                else:
                    setattr(obj, k, v[0])
            else:
                if type(v) == str:
                    setattr(obj, k, v.decode('utf-8'))
                else:
                    setattr(obj, k, v)
        return obj


class ApiHandler(BaseHandler):

    
    def __init__(self, *argc, **argkw):
        super(ApiHandler, self).__init__(*argc, **argkw)

    def render_json(self, **template_vars):
        if not template_vars.has_key("code"):
            template_vars["code"] = 0
        resp = json.dumps(template_vars, ensure_ascii=False)
        self.write(resp)

    def parse_form_request(self):
        try:
            sid = self.get_argument("sid")
            return apiutils.parse_form_request(self.get_secret(sid), self.get_params())
        except Exception as err:
            logger.error(u"api authorize parse error, %s" % utils.safeunicode(traceback.format_exc()))
            raise ValueError(u"Error: %s" % utils.safeunicode(err.message))


    def _decode_msg(self,err, msg):
        _msg = msg and utils.safeunicode(msg) or ''
        if issubclass(type(err),BaseException):
            return u'{0}, {1}'.format(utils.safeunicode(_msg),utils.safeunicode(err.message))
        else:
            return _msg

    def render_success(self, msg=None, **result):
        self.render_json(code=apistatus.success.code,
            msg=self._decode_msg(None,msg or apistatus.success.msg),**result)

    def render_sign_err(self, err=None, msg=None):
        self.render_json(code=apistatus.sign_err.code,
            msg=self._decode_msg(err,msg or apistatus.sign_err.msg))
 
    def render_parse_err(self, err=None, msg=None):
        self.render_json(code=apistatus.sign_err.code, 
            msg=self._decode_msg(err,msg or apistatus.sign_err.msg))
 
    def render_verify_err(self, err=None,msg=None):
        self.render_json(code=apistatus.verify_err.code, 
            msg=self._decode_msg(err,msg or apistatus.verify_err.msg))
 
    def render_server_err(self,err=None, msg=None):
        self.render_json(code=apistatus.server_err.code, 
            msg=self._decode_msg(err,msg or apistatus.server_err.msg))

    def render_timeout(self,err=None, msg=None):
        self.render_json(code=apistatus.timeout.code, 
            msg=self._decode_msg(err,msg or apistatus.timeout))

    def render_limit_err(self,err=None, msg=None):
        self.render_json(code=apistatus.limit_err.code, 
            msg=self._decode_msg(err,msg or apistatus.limit_err)) 

    def render_unknow(self,err=None, msg=None):
        self.render_json(code=apistatus.unknow.code, 
            msg=self._decode_msg(err,msg or apistatus.unknow))



def authenticated(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                self.set_header('Content-Type', 'application/json; charset=UTF-8')
                self.write(json.dumps({'code': 1, 'msg': 'session expire'}))
                return
            if self.request.method in ("GET", "POST", "HEAD"):
                url = self.get_login_url()
                if "?" not in url:
                    if urlparse.urlsplit(url).scheme:
                        # if login url is absolute, make next absolute too
                        next_url = self.request.full_url()
                    else:
                        next_url = self.request.uri
                    url += "?" + urlencode(dict(next=next_url))
                self.redirect(url)
                return
            return self.render_error(msg=u"Unauthorized access")
        else:
            return method(self, *args, **kwargs)
    return wrapper


