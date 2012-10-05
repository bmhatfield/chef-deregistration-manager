#!/usr/bin/env python
from distutils.core import setup
import platform

version = "1.0.2"

if platform.dist()[0] == 'Ubuntu':
    distro = 'debian'
else:
    distro = platform.dist()[0]

setup(name="chef-registration",
      version=version,
      description="Chef Client Deregestration for Dynamic, Autoscaled Cloud Environments",
      author="Brian Hatfield",
      author_email="bmhatfield@gmail.com",
      url="https://github.com/bmhatfield/chef-deregistration-manager",
      packages=['clientqueue', 'message'],
      package_dir={'': 'lib'},
      data_files=[('/etc/init.d/', ["init/%s/registration-server" % distro, "init/%s/registration-client" % distro]),
                  ("/etc/chef-registration/server", ["registration-server/example.cfg"]),
                  ("/etc/chef-registration/client", ["registration-client/example.cfg"])
                 ],
      scripts=["registration-server/registration-server", "registration-client/registration-client"]
    )
