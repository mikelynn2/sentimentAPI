#!/usr/bin/python


import multiprocessing

bind = "0.0.0.0:8000"

# one worker per core is ideal.
workers = multiprocessing.cpu_count()

backlog = 2048

'''
using gevent for async
performance seems 10-20% better under gevent then sync
if you have problems with gevent, you can switch to sync by uncommenting 'sync'
and commenting out "worker_class='gevent'" and "worker_connections"
'''
#worker_class = 'sync'
#worker_class = 'eventlet'
worker_class = 'gevent'
worker_connections = 3000

max_requests = 40000
max_requests_jitter = 5000

timeout = 30
graceful_timeout = 30

keepalive = 2

limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8091

preload_app = True

#daemon = False
daemon = True

accesslog = 'access.log'
errorlog = 'error.log'

