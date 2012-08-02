#!/usr/bin/env python
#
#
#
APPLICATION_VERSION=0.3

import os
import sys
import optparse
import configobj

# A temporary hack while this is in development
if os.path.isdir("/Users/bhatfield/Documents/dev"):
    sys.path.append("lib")

import clientqueue.queue
import message

# Read Command Line Options
parser = optparse.OptionParser(usage="%prog [options]", version="%prog " + str(APPLICATION_VERSION))
parser.add_option("-c", "--config", dest="config", default="/etc/chef-registration/client.cfg", help="Configuration file path")
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Log extra debug output")
parser.add_option("-d", "--dry-run", action="store_true", dest="dry_run", default=False, help="Don't actually delete nodes/clients from chef server")
(options, args) = parser.parse_args()

# Create Configuration Defaults
defaults = {
    'aws': {'secret_key': None, 'access_key': None},
    'queue': {'queue_name': None, 'queue_id': None}
}

config = configobj.ConfigObj()
config.merge(defaults)

if os.path.exists(options.config):
    user_config = configobj.ConfigObj(options.config, unrepr=True)
    config.merge(user_config)
else:
    print "Configuration file '%s' not found." % (options.config)
    sys.exit(1)

msg = message.Message({'type': 'registration', 'method': 'deregister', 'nagios_name': 'imarlier-vagrant-ubuntu-box', 'chef_name': 'imarlier-vagrant-ubuntu-box'})

if not options.dry_run:
    q = clientqueue.queue.SQSQueue("%s-%s" % (config['queue']['queue_name'], config['queue']['queue_id']), config['aws']['access_key'], config['aws']['secret_key'])
    q.enqueue(msg)
else:
    print("Message: %s" %(msg))