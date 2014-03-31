
import os
from setuptools import setup

setup(
  name="rwrapper",
  version="1.0.1",
  description="This package provides an ORM layer for RethinkDB",
  url="https://github.com/dparlevliet/rwrapper",
  maintainer="dparlevliet",
  packages=['rwrapper'],
  install_requires=['rethinkdb', 'jsonpickle']
)