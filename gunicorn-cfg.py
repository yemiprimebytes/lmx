# -*- encoding: utf-8 -*-

bind = '0.0.0.0:6500'
workers = 3
accesslog = '-'
loglevel = 'debug'
capture_output = True
enable_stdio_inheritance = True
# Added by Prime
command= '/home/django/blackboard/env/bin/gunicorn'
pythonpath='/home/django/blackboard'

# Server settings
errorlog = "/home/django/blackboard/gunicorn.error"
accesslog = "/home/django/blackboard/gunicorn.access"
