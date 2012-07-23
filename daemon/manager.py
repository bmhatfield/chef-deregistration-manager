import time
import json
import sys

sys.path.append("/Users/bhatfield/Documents/dev/NagiosCGI")
import nagcgi
import clientqueue.queue

# TODO: Argparse/optparse

# TODO: Configuration File (credentials, etc)

# TODO: Daemonize

# Configure Nagios CGI Client
nagios = nagcgi.Nagcgi('tools.qanet.local', userid='cgiservice', password='', debug=True)

# Configure Deregistration Queue Client
q = clientqueue.queue.SQSQueue('chef-client-deregistration-queue-arctic', 'ACCESS_KEY', 'SECRET_KEY')

while True:
    if len(q) > 0:
        rawmessage = q.dequeue()

        message = json.loads(rawmessage)

        if message["type"] == "deregistration":
            nagios.schedule_host_downtime(hostname=message["client_name"])

            # TODO: Dump Chef Node JSON via API
            # TODO: Remove Chef Node via API
            # TODO: Remove Chef Client via API

        # Skip sleep if an action was taken (process all events straight away)    
        continue

    time.sleep(3)
