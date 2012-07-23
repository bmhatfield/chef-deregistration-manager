#import clientqueue.queue

#q = clientqueue.queue.SQSQueue('chef-client-deregistration-queue-arctic', 'ACCESS_KEY', 'SECRET_KEY')

#q.enqueue("test message")

#print q.dequeue()

import nagios.nagcgi

nagios = nagios.nagcgi.Nagcgi('monitor', userid='nagiosapi', password='', secure=True)

nagios.schedule_host_downtime(hostname="")
