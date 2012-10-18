chef-deregistration-manager
===========================

**Queue Based Chef Client Deregistration for the Cloud**

Building Debian Packages
------------------------
    sudo aptitude install build-essential git python-stdeb
    git clone https://github.com/bmhatfield/chef-deregistration-manager.git
    cd chef-deregistration-manager
    python setup.py --command-packages=stdeb.command bdist_deb

chef-deregistration-manager
---------------------------
Dependencies:
  python-setuptools
  python-configobj
  python-boto (2+)
  python-pychef (https://github.com/coderanger/pychef)
  python-nagcgi (https://github.com/bmhatfield/NagiosCGI)

    Polls SQS
        If the queue does not exist:
            Create queue - The name is a combination of queue_name and id, both configurable

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



chef-registration-init (clients)
--------------------------------

    stop():
      if runlevel == 0:
        Issue SNS message to delete node


FAQ
---------------

Q: It won't start.  
A: Make sure that the dependencies are installed, and that you've created server.cfg and client.cfg (the install creates example.cfg)  

Q: Why would I put my AWS credentials on every host?! That's insecure!  
A: We use IAM to create credentials that only have permission to publish to the relevant queue. The server's credentials will need the ability to create and manage SNS endpoints as well as SQS queues, as well.  



More information
----------------
This code based upon:

    http://www.nuvolesystems.com/2012/07/02/chef-node-de-registration-for-autoscaling-groups/
