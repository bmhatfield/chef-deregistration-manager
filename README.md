chef-deregistration-manager
===========================

**Queue Based Chef Client Deregistration for the Cloud**

Building Debian Packages
------------------------
    sudo aptitude install build-essential git python-stdeb
    git clone https://github.com/bmhatfield/chef-deregistration-manager.git
    python setup.py --command-packages=stdeb.command bdist_deb

chef-deregistration-manager
---------------------------
    Polls SQS
        If the queue for the datacenter does not exist:
            Create queue

        If there are events:
            Grab event.

            If the event is a 'delete':
                Put instance in downtime in Nagios
                Dump Chef node JSON to disk
                Remove Chef Node via Chef API
                Remove Chef Client via Chef API

                If there are no more events:
                    Trigger chef-client run

            If the event is an 'ensure':
                Fire Alert
                Recreate Node in Chef



chef-registration-init
----------------------
    start():
        Issue SNS message to ensure that the client is registered.

    stop():
        Issue SNS message to delete node
        If success, delete client.pem




sqs-alarm
---------
    Use the Alarm Code specified here:
        http://www.nuvolesystems.com/2012/07/02/chef-node-de-registration-for-autoscaling-groups/