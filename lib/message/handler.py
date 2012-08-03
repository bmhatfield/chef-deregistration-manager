import os
import sys
import logging
import json

# A temporary hack while this is in development
if os.path.isdir("/Users/bhatfield/Documents/dev"):
    sys.path.append("/Users/bhatfield/Documents/dev/pychef")

import chef


class ChefRegistrationHandler():

    def __init__(self, chef_api, backup_dir):
        self.api = chef_api
        self.backup_dir = backup_dir

    def process(self, message):
        if message.message["type"] == "registration" and message.message["method"] == "deregister":
            self.deregister(message)

    def backup(self, filename, contents):
        if os.path.exists(self.backup_dir) and os.path.isdir(self.backup_dir):
            logging.info("Writing backup: %s", os.path.join(self.backup_dir, filename))
            handle = open(os.path.join(self.backup_dir, filename), 'w')
            handle.write(contents)
            return True
        else:
            raise RuntimeError("Unable to access backup path: '%s'" % (self.backup_dir))

    def deregister(self, message):
        try:
            node = chef.Node(message.message["chef_name"])
            if self.backup("chef-node-%s" % (message.message["chef_name"]), json.dumps(node.attributes.to_dict())):
                node.delete()
        except chef.exceptions.ChefServerNotFoundError:
            logging.error("Node removal requested for non-existent chef node '%s'", message.message["chef_name"])
        except Exception as e:
            logging.exception("Exception while deleting chef node:\n %s", str(e))

        try:
            client = chef.Client(message.message["chef_name"])
            if self.backup("chef-client-%s" % (message.message["chef_name"]), json.dumps(client.to_dict())):
                client.delete()
        except chef.exceptions.ChefServerNotFoundError:
            logging.error("Client removal requested for non-existent chef client '%s'", message.message["chef_name"])
        except Exception as e:
            logging.exception("Exception while deleting chef client:\n %s", str(e))

