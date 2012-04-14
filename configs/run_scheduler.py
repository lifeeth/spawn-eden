#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
if '__file__' in globals():
    path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(path)
else:
    path = os.getcwd() # Seems necessary for py2exe
sys.path = [path]+[p for p in sys.path if not p==path]
# import gluon.import_all ##### This should be uncommented for py2exe.py
import gluon.widget
from gluon.shell import run
# Start Web2py Scheduler -- Note the app name is hardcoded!
if __name__ == '__main__':
    run('eden',True,True,None,False,"from gluon import current; current._scheduler.loop()")
