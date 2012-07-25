#!/usr/bin/env python
#
# This application daemonizes and listens to a queue for specifically crafted events.
# It will then process the event according to type, such as "deregistration", which
# implies certain actions such as Nagios downtime, Chef Client deregistration, etc.
#
APPLICATION_VERSION=0.1

import os
import sys
import time
import json
import optparse
import configobj

# Required for importing nagcgi, if not installed
sys.path.append("/Users/bhatfield/Documents/dev/NagiosCGI")

# Required for importing pychef, if not installed
sys.path.append("/Users/bhatfield/Documents/dev/pychef")

import clientqueue.queue
import nagcgi
import chef

# Read Command Line Options
parser = optparse.OptionParser(usage="%prog [options] config_file", version="%prog " + str(APPLICATION_VERSION))
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Log extra debug output")
parser.add_option("-d", "--dry-run", action="store_true", dest="dry_run", default=False, help="Don't actually delete nodes/clients from chef server")
(options, args) = parser.parse_args()

if len(args) < 1:
    print "Required argument: config_file"
    sys.exit(1)
else:
    config_file = args[0]

# Create Configuration Defaults
defaults = {
    'general': {'daemon': True},
    'aws': {'secret_key': None, 'access_key': None},
    'queue': {'queue_name': None, 'queue_id': None, 'poll_interval': 15},
    'nagios': {'use': True, 'host': 'monitor', 'username': 'cgiservice', 'password': None},
    'chef': {'host': 'localhost', 'key': 'client.pem', 'client': None}
}

config = configobj.ConfigObj()
config.merge(defaults)

if os.path.exists(config_file):
    user_config = configobj.ConfigObj(config_file)
    config.merge(user_config)
else:
    print "Configuration file %s not found. This application requires some configuration settings to be set." % (config_file)
    sys.exit(1)

if options.verbose:
    print "Running with the following config settings: \n %s" % (config)

# Configure Chef API Client
try:
    if config['chef']['host'] is not None and config['chef']['key'] is not None and config['chef']['client'] is not None:
        api = chef.ChefApi(config['chef']['host'], config['chef']['key'], config['chef']['client'])
    else:
        api = chef.autoconfigure()
except:
    print "Could not configure Chef Client." # TODO: Create Log message instead.
    sys.exit(1)

# TODO: Daemonize
# Diamond/bin/diamond source
# -or-
# http://pypi.python.org/pypi/python-daemon/

# Configure Nagios CGI Client
nagios = nagcgi.Nagcgi(config['nagios']['host'], userid=config['nagios']['username'], password=config['nagios']['password'], debug=options.verbose)

# Configure Deregistration Queue Client
q = clientqueue.queue.SQSQueue("%s-%s" % (config['queue']['queue_name'], config['queue']['queue_id']), 
                                config['queue']['access_key'], config['queue']['secret_key'])

# Control Variable
trigger_chef_run = False

while True:
    if len(q) > 0:
        rawmessage = q.dequeue()

        # http://docs.python.org/library/json.html
        message = json.loads(rawmessage)

        if message["type"] == "deregistration":

            if config['nagios']['use']:
                nagios.schedule_host_downtime(hostname=message["nagios_name"])

            # Create Chef Node Object:
            node = chef.Node(message["chef_name"])

            # Dump Chef Node JSON via API
            json.dumps(node.attributes.to_dict()) # TODO: Output to file

            # Remove Chef Node via API
            if not options.dry_run:
                node.delete()

            # Create Chef Client Object
            client = chef.Client(message["chef_name"])

            # Dump Chef Client JSON via API
            json.dumps(client.to_dict()) # TODO: Output to file

            # Remove Chef Client via API
            if not options.dry_run:
                client.delete()

            # Make sure to tell Chef to run.
            trigger_chef_run = True
    else:
        if trigger_chef_run:
            # TODO: Spin off a subprocess for a chef-client run,
            #       assuming we are on a monitor server (async? sync?)
            print "Triggering chef-client run!" # TODO: Create Log message instead.
            trigger_chef_run = False

        # Go to sleep if there was nothing in the queue.
        time.sleep(config['queue']['poll_interval'])
