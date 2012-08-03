#!/usr/bin/env python
from distutils.core import setup
import platform

#distro = platform.dist()[0]
distro = 'debian'
version = "0.7"

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
