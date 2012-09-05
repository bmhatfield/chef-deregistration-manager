import os
import logging
import json
import chef
import time


class ChefRegistrationHandler():

    def __init__(self, chef_api, backup_dir):
        self.api = chef_api
        self.backup_dir = backup_dir

    def process(self, message):
        if message.format.__class__.__name__ == "AutoscalingMessage":
            nodes = chef.Search("node", q="instance_id:%s" % (message.message['EC2InstanceId']))
            if nodes.total == 1:
                self._remove(chef_name=nodes[0]['name'], instance_id=message.message['EC2InstanceId'])
            else:
                raise ValueError("API Returned %s nodes, expected 1" % (nodes.total))

        elif message.format.__class__.__name__ == "RegistrationMessage":
            if message.message["method"] == "deregister":
                if 'instance_id' in message.message:
                    instance_id = message.message['instance_id']
                else:
                    instance_id = None

                self._remove(chef_name=message.message['chef_name'], instance_id=instance_id)

        else:
            raise NotImplementedError("Unable to process message type: %s" % (message.format.__class__.__name__))

    def _remove(self, chef_name, instance_id=None, backup=True):
        try:
            client = chef.Client(chef_name)
            if backup and self._backup("chef-client-%s" % (chef_name), json.dumps(client.to_dict())):
                client.delete()
        except chef.exceptions.ChefServerNotFoundError:
            logging.error("Client removal requested for non-existent chef client '%s'", chef_name)
        except Exception as e:
            logging.exception("Exception while deleting chef client:\n %s", str(e))

        try:
            node = chef.Node(chef_name)
            if instance_id:
                if node.attributes["ec2"]["instance_id"] != instance_id:
                    raise ValueError("Instance ID (%s) does not match attribute ID (%s)" %
                                    (instance_id, node.attributes["ec2"]["instance_id"]))

            if backup and self._backup("chef-node-%s" % (chef_name), json.dumps(node.attributes.to_dict())):
                node.delete()
        except chef.exceptions.ChefServerNotFoundError:
            logging.error("Node removal requested for non-existent chef node '%s'", chef_name)
        except Exception as e:
            logging.exception("Exception while deleting chef node:\n %s", str(e))

    def _backup(self, filename, contents):
        if os.path.exists(self.backup_dir) and os.path.isdir(self.backup_dir):
            logging.info("Writing backup: %s", os.path.join(self.backup_dir, filename))
            handle = open(os.path.join(self.backup_dir, "%s-%s" % (filename, int(time.time()))), 'w')
            handle.write(contents)
            return True
        else:
            raise RuntimeError("Unable to access backup path: '%s'" % (self.backup_dir))
