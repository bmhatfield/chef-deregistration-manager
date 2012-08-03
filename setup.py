#!/usr/bin/env python
from distutils.core import setup
import platform
import shutil
import os

version = "0.7"

if platform.dist()[0] == 'Ubuntu':
    distro = 'debian'
elif platform.uname()[0] == 'Darwin':
    distro = 'debian'  # A little hack for Mac testing
else:
    distro = platform.dist()[0]

setup(name="chef-registration-server",
      version=version,
      description="Chef Client Cloud Registration Management Server",
      author="Brian Hatfield",
      author_email="bmhatfield@gmail.com",
      url="https://github.com/bmhatfield/chef-deregistration-manager",
      packages=['clientqueue', 'message'],
      package_dir={'': 'lib'},
      data_files=[('/etc/init.d/', ["init/%s/registration-server" % distro]),
                  ("/etc/chef-registration/server", ["registration-server/example.cfg"])],
      scripts=["registration-server/registration-server"]
    )

if os.path.isdir("deb_dist/chef-registration-server-%s" % (version)):
    shutil.rmtree("deb_dist/chef-registration-server-%s" % (version))

setup(name="chef-registration-client",
      version=version,
      description="Chef Client Cloud Registration Client",
      author="Brian Hatfield",
      author_email="bmhatfield@gmail.com",
      url="https://github.com/bmhatfield/chef-deregistration-manager",
      packages=['clientqueue', 'message'],
      package_dir={'': 'lib'},
      data_files=[('/etc/init.d/', ["init/%s/registration-client" % distro]),
                  ("/etc/chef-registration/client", ["registration-client/example.cfg"])],
      scripts=["registration-client/registration-client"]
    )
