#!/usr/bin/env python
#
# This application daemonizes and listens to a queue for specifically crafted events.
# It will then process the event according to type, such as "deregistration", which
# implies certain actions such as Nagios downtime, Chef Client deregistration, etc.
#
APPLICATION_VERSION = 0.7

import os
import sys
import time
import logging
import optparse
import configobj

# A temporary hack while this is in development
if os.path.isdir("/Users/bhatfield/Documents/dev"):
    sys.path.append("/Users/bhatfield/Documents/dev/NagiosCGI")
    sys.path.append("/Users/bhatfield/Documents/dev/pychef")
    sys.path.append("lib")

import clientqueue.queue
import message
import nagcgi
import chef

# Read Command Line Options
parser = optparse.OptionParser(usage="%prog [options]", version="%prog " + str(APPLICATION_VERSION))
parser.add_option("-c", "--config", dest="config", default="/etc/chef-registration/server.cfg", help="Configuration file path")
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Log extra debug output")
parser.add_option("-d", "--dry-run", action="store_true", dest="dry_run", default=False, help="Don't actually delete nodes/clients from chef server")
(options, args) = parser.parse_args()

if os.path.exists(options.config):
    config = configobj.ConfigObj()
    user_config = configobj.ConfigObj(options.config, unrepr=True)
    defaults = {
        'general': {'daemon': False, 'pidfile': 'manager.pid', 'backup_dir': 'backups'},
        'aws': {'secret_key': None, 'access_key': None},
        'queue': {'queue_name': None, 'queue_id': None, 'poll_interval': 15},
        'nagios': {'use': True, 'host': 'monitor', 'username': 'cgiservice', 'password': None},
        'chef': {'host': 'localhost', 'key': 'client.pem', 'client': None}
    }
    config.merge(defaults)
    config.merge(user_config)
else:
    print "Configuration file '%s' not found." % (options.config)
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

    logging.info("Running against the following chef server: %s" % (api.url))
except:
    logging.error("Could not configure Chef Client.")
    sys.exit(1)

# Configure ChefRegistrationHandler
messagehandler = message.ChefRegistrationHandler(api, backup_dir=config['general']['backup_dir'])

# Configure Nagios CGI Client
if config['nagios']['use']:
    logging.debug("Configuring Nagios Client: ", config['nagios'])
    nagios = nagcgi.Nagcgi(config['nagios']['host'], userid=config['nagios']['username'], password=config['nagios']['password'], debug=options.verbose)

# Configure Deregistration Queue Client
logging.debug("Configuring Queue Client: ", config['queue'])
q = clientqueue.queue.SQSQueue("%s-%s" % (config['queue']['queue_name'], config['queue']['queue_id']), config['aws']['access_key'], config['aws']['secret_key'])


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
        pf = file(config['general']['pidfile'], 'w+')
        pf.write("%s\n" % pid)
        pf.close()
        logging.debug("Wrote child PID file: %s" % (config['general']['pidfile']))
    except IOError, e:
        logging.error("Failed to write child PID file: %s" % (e))
        sys.exit(1)


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

                    if not options.dry_run:
                        if config['nagios']['use']:
                            logging.info("Scheduling Nagios downtime for %s", msg.message["nagios_name"])
                            nagios.schedule_host_downtime(hostname=msg.message["nagios_name"])

                        messagehandler.process(msg)
                        trigger_chef_run = True
                else:
                    logging.warning("Disregarding empty message from queue. (SQS bug due to fast re-poll of queue.)")
                    continue
            except Exception as e:
                logging.exception("Exception while processing message:\n %s", str(e))
                continue
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
