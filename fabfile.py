#!/usr/bin/env python
#coding:utf-8
import sys,os
sys.path.insert(0,os.path.dirname(__file__))
from fabric.api import *
from txweb import __version__

def push():
    message = raw_input(u"input git commit message:")
    local("git add .")
    try:
        local("git commit -m \'%s: %s\'"%(__version__,message or 'no commit message'))
        local("git push origin master")
        local("git push coding master")
    except:
        print u'no commit'