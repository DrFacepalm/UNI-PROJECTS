# DO NOT TOUCH UNLESS YOU KNOW WHAT YOU ARE DOING
#
# This file sets up Python to be able to import packages from our
# modules directory, which contains our vendored packages.
#
# Don't touch this unless you have flask and pg8000 installed.

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))
