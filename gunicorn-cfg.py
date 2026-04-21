# -*- encoding: utf-8 -*-

bind = "unix:/run/gunicorn/lmx.sock"
workers = 3
accesslog = '-'
loglevel = 'debug'
capture_output = True
enable_stdio_inheritance = True
# Added by Prime
command= '/home/django/lmx/env/bin/gunicorn'
pythonpath='/home/django/lmx'

# Server settings
errorlog = "/home/django/lmx/gunicorn.error"
accesslog = "/home/django/lmx/gunicorn.access"
