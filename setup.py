#!/usr/bin/env python

# Author: Dan Walsh <dwalsh@redhat.com>
import sys
import os
from distutils.core import setup

sys.path.insert(0, os.path.abspath(os.getcwd()))
from Atomic import __version__

setup(
    name="atomic", scripts=["atomic", "atomic_dbus.py"],
    version=__version__,
    description="Atomic Management Tool",
    author="Daniel Walsh", author_email="dwalsh@redhat.com",
    packages=["Atomic"],
    data_files=[('/etc/dbus-1/system.d/', ["org.atomic.conf"]),
                ('/usr/share/dbus-1/system-services', ["org.atomic.service"]),
                ('/usr/share/polkit-1/actions/', ["org.atomic.policy"]),
                ("/usr/share/bash-completion/completions/",
                 ["bash/atomic"])]
)
