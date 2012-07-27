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
import logging
import optparse
import traceback
import configobj

# Required for importing nagcgi, if not installed
sys.path.append("/Users/bhatfield/Documents/dev/NagiosCGI")

# Required for importing pychef, if not installed
sys.path.append("/Users/bhatfield/Documents/dev/pychef")

import clientqueue.queue
import message
import nagcgi
import chef

# TODO: Configure Logging
logging.basicConfig(level=logging.INFO)

# Read Command Line Options
parser = optparse.OptionParser(usage="%prog [options] config_file", version="%prog " + str(APPLICATION_VERSION))
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Log extra debug output")
parser.add_option("-d", "--dry-run", action="store_true", dest="dry_run", default=False, help="Don't actually delete nodes/clients from chef server")
(options, args) = parser.parse_args()

if len(args) < 1:
    logging.error("Required argument: config_file")
    sys.exit(1)
else:
    config_file = args[0]

# Create Configuration Defaults
defaults = {
    'general': {'daemon': False},
    'aws': {'secret_key': None, 'access_key': None},
    'queue': {'queue_name': None, 'queue_id': None, 'poll_interval': 15},
    'nagios': {'use': True, 'host': 'monitor', 'username': 'cgiservice', 'password': None},
    'chef': {'host': 'localhost', 'key': 'client.pem', 'client': None}
}

config = configobj.ConfigObj()
config.merge(defaults)

if os.path.exists(config_file):
    user_config = configobj.ConfigObj(config_file, unrepr=True)
    config.merge(user_config)
    logging.info("Running with the following config settings:\n%s\n%s", config, options)
else:
    logging.error("Configuration file '%s' not found.", config_file)
    sys.exit(1)

# Configure Chef API Client
try:
    if config['chef']['host'] is not None and config['chef']['key'] is not None and config['chef']['client'] is not None:
        api = chef.ChefApi(config['chef']['host'], config['chef']['key'], config['chef']['client'])
    else:
        api = chef.autoconfigure()
except:
    logging.error("Could not configure Chef Client.")
    sys.exit(1)

def daemonize():
    # Daemonize (http://code.activestate.com/recipes/278731/)
    logging.info("Daemonizing...")
    try:
        pid = os.fork()
        if pid > 0:
            # Exit first parent
            sys.exit(0)
    except OSError, e:
        sys.stderr.write("Failed to fork process." % (e))
        sys.exit(1)

    # Decouple from parent environment
    os.setsid()
    os.umask(0)

    # Fork 2
    try:
        pid = os.fork()
        if pid > 0:
            # Exit second parent
            sys.exit(0)
    except OSError, e:
        sys.stderr.write("Failed to fork process." % (e))
        sys.exit(1)

    # Close file descriptors so that we can detach
    sys.stdout.close()
    sys.stderr.close()
    sys.stdin.close()
    os.close(0)
    os.close(1)
    os.close(2)


# Configure Nagios CGI Client
if config['nagios']['use']:
    logging.debug("Configuring Nagios Client: ", config['nagios'])
    nagios = nagcgi.Nagcgi(config['nagios']['host'], userid=config['nagios']['username'], 
                            password=config['nagios']['password'], debug=options.verbose)

# Configure Deregistration Queue Client
logging.debug("Configuring Queue Client: ", config['queue'])
q = clientqueue.queue.SQSQueue("%s-%s" % (config['queue']['queue_name'], config['queue']['queue_id']), 
                                config['aws']['access_key'], config['aws']['secret_key'])


if config['general']['daemon']:
    daemonize()

# Control Variable
trigger_chef_run = False

while True:
    logging.debug("Waking up queue poll cycle.")

    if len(q) > 0:
        try:
            rawmessage = q.dequeue()
            logging.info("Message found: \n %s", rawmessage)
            msg = message.Message(rawmessage)
        except Exception as e:
            logging.exception("Exception while loading message:\n %s", str(e))
            continue

        if msg.message["type"] == "registration":
            if config['nagios']['use']:
                logging.info("Scheduling Nagios downtime for %s", msg.message["nagios_name"])
                nagios.schedule_host_downtime(hostname=msg.message["nagios_name"])

            # Create Chef Node Object:
            node = chef.Node(msg.message["chef_name"])

            # Dump Chef Node JSON via API
            json.dumps(node.attributes.to_dict()) # TODO: Output to file

            # Remove Chef Node via API
            if not options.dry_run:
                node.delete()

            # Create Chef Client Object
            client = chef.Client(msg.message["chef_name"])

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
            logging.debug("Triggering chef-client run!")
            trigger_chef_run = False

        # Go to sleep if there was nothing in the queue.
        logging.debug("Nothing to do. Sleeping for %s secs.", config['queue']['poll_interval'])
        time.sleep(float(config['queue']['poll_interval']))
