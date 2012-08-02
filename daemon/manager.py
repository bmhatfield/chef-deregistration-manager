#!/usr/bin/env python
#
# This application daemonizes and listens to a queue for specifically crafted events.
# It will then process the event according to type, such as "deregistration", which
# implies certain actions such as Nagios downtime, Chef Client deregistration, etc.
#
APPLICATION_VERSION=0.2

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
    'general': {'daemon': False, 'pidfile': 'manager.pid', 'backup_dir': 'backups'},
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
else:
    print "Configuration file '%s' not found." % (config_file)
    sys.exit(1)


# Configure Logging
if config['general']['daemon']:
    logging.basicConfig(level=logging.INFO, filename='manager.log')
else:
    logging.basicConfig(level=logging.INFO)


# Write out configuration values
logging.info("Running with the following config settings:\n%s\n%s", config, options)


# Configure Chef API Client
try:
    if config['chef']['host'] is not None and config['chef']['key'] is not None and config['chef']['client'] is not None:
        api = chef.ChefApi(config['chef']['host'], config['chef']['key'], config['chef']['client'])
    else:
        api = chef.autoconfigure()

    logging.info("Running against the following chef server:" )
except:
    logging.error("Could not configure Chef Client.")
    sys.exit(1)


# Configure Nagios CGI Client
if config['nagios']['use']:
    logging.debug("Configuring Nagios Client: ", config['nagios'])
    nagios = nagcgi.Nagcgi(config['nagios']['host'], userid=config['nagios']['username'], 
                            password=config['nagios']['password'], debug=options.verbose)


# Configure Deregistration Queue Client
logging.debug("Configuring Queue Client: ", config['queue'])
q = clientqueue.queue.SQSQueue("%s-%s" % (config['queue']['queue_name'], config['queue']['queue_id']), 
                                config['aws']['access_key'], config['aws']['secret_key'])


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

    try:
        pid = str(os.getpid())
        pf = file(config['general']['pidfile'],'w+')
        pf.write("%s\n" % pid)
        pf.close()
        logging.debug("Wrote child PID file: %s" % (config['general']['pidfile']))
    except IOError, e:
        logging.error("Failed to write child PID file: %s" % (e))
        sys.exit(1)

def write_backup(filename, contents, backup_dir=config['general']['backup_dir']):
    if os.path.exists(backup_dir) and os.path.isdir(backup_dir):
        logging.info("Writing backup: %s", os.path.join(backup_dir, filename))
        handle = open(os.path.join(backup_dir, filename), 'w')
        handle.write(contents)
        return True
    else:
        raise RuntimeError("Unable to access backup path: '%s'" % (backup_dir))

def main():
    # Control Variable
    trigger_chef_run = False

    while True:
        logging.debug("Waking up queue poll cycle.")

        if len(q) > 0:
            try:
                rawmessage = q.dequeue()
                if len(rawmessage) > 0:
                    logging.info("Message found:\n%s", rawmessage)
                    msg = message.Message(rawmessage)
                else:
                    logging.warning("Disregarding empty message from queue. (SQS bug due to fast re-poll of queue.)")
                    continue
            except Exception as e:
                logging.exception("Exception while loading message:\n %s", str(e))
                continue

            if msg.message["type"] == "registration" and msg.message["method"] == "deregister":
                if config['nagios']['use']:
                    logging.info("Scheduling Nagios downtime for %s", msg.message["nagios_name"])
                    nagios.schedule_host_downtime(hostname=msg.message["nagios_name"])

                try:
                    # Create Chef Node Object
                    node = chef.Node(msg.message["chef_name"])

                    # Dump Chef Node JSON via API, write to backup.
                    if write_backup("chef-node-%s" % (msg.message["chef_name"]), json.dumps(node.attributes.to_dict())):
                        if not options.dry_run:
                            node.delete()   # Remove Chef Node via API
                except Exception as e:
                    logging.exception("Exception while deleting chef node:\n %s", str(e))

                try:
                    # Create Chef Client Object
                    client = chef.Client(msg.message["chef_name"])

                    # Dump Chef Client JSON via API, write to backup.
                    if write_backup("chef-client-%s" % (msg.message["chef_name"]), json.dumps(client.to_dict())):
                        if not options.dry_run:
                            client.delete() # Remove Chef Client via API
                except Exception as e:
                    logging.exception("Exception while deleting chef client:\n %s", str(e))

                # Make sure to tell Chef to run
                trigger_chef_run = True
        else:
            if trigger_chef_run:
                # TODO: Spin off a subprocess for a chef-client run,
                #       assuming we are on a monitor server (async? sync?)
                logging.info("Triggering chef-client run!")
                trigger_chef_run = False

            # Go to sleep if there was nothing in the queue.
            logging.debug("Nothing to do. Sleeping for %s secs.", config['queue']['poll_interval'])
            time.sleep(config['queue']['poll_interval'])

if config['general']['daemon']:
    daemonize()

main()
