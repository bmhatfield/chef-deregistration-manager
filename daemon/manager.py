import time
import json
import sys
import ConfigParser

# Required for importing nagcgi, if not installed
sys.path.append("/Users/bhatfield/Documents/dev/NagiosCGI")

# Required for importing pychef, if not installed
sys.path.append("/Users/bhatfield/Documents/dev/pychef")

import clientqueue.queue
import nagcgi
import chef

# Create Constants (that can be modified by config / command line)
WAKE_INTERVAL = 15

# TODO: Argparse/optparse

# TODO: Configuration File (credentials, etc)
# http://docs.python.org/library/configparser.html
config = ConfigParser.RawConfigParser()
config.read('defaults.cfg')


# Configure Chef API Client
api = chef.autoconfigure()  # TODO: Create API object with values in configuration file instead

sys.exit(0)

# TODO: Daemonize
# Diamond/bin/diamond source
# -or-
# http://pypi.python.org/pypi/python-daemon/

# Configure Nagios CGI Client
nagios = nagcgi.Nagcgi('tools.qanet.local', userid='cgiservice', password='', debug=True)

# Configure Deregistration Queue Client
q = clientqueue.queue.SQSQueue('chef-client-deregistration-queue-arctic', 'ACCESS_KEY', 'SECRET_KEY')

# Initialize Control Variable
trigger_chef_run = False

while True:
    if len(q) > 0:
        rawmessage = q.dequeue()

        # http://docs.python.org/library/json.html
        message = json.loads(rawmessage)

        if message["type"] == "deregistration":
            nagios.schedule_host_downtime(hostname=message["nagios_name"])

            # Create Chef Node Object:
            node = chef.Node(message["chef_name"])

            # Dump Chef Node JSON via API
            json.dumps(node.attributes.to_dict()) # TODO: Output to file

            # Remove Chef Node via API
            node.delete()

            # Create Chef Client Object
            client = chef.Client(message["chef_name"])

            # Dump Chef Client JSON via API
            json.dumps(client.to_dict()) # TODO: Output to file

            # Remove Chef Client via API
            client.delete()

            # Make sure to tell Chef to run.
            trigger_chef_run = True
    else:
        if trigger_chef_run:
            # TODO: Spin off a subprocess for a chef-client run,
            #       assuming we are on a monitor server (async? sync?)
            print "Triggering chef-client run!"

        # Go to sleep if there was nothing in the queue.
        time.sleep(WAKE_INTERVAL)
