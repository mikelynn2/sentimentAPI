#!/usr/bin/python


import multiprocessing

bind = "0.0.0.0:8000"

# one worker per core is ideal.
workers = multiprocessing.cpu_count()

backlog = 2048


# if you want lightweight threads install gevent 
# I haven't seen them be much faster
# but install and then switch worker_class to gevent below
#sudo pip install -U gevent

worker_class = 'sync'
#worker_class = 'eventlet'
#worker_class = 'gevent'
#worker_connections = 3000

max_requests = 100000
max_requests_jitter = 10000

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
