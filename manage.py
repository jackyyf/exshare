#!/usr/bin/env python

from gevent import monkey; monkey.patch_all(); del monkey
from psycogreen.gevent import patch_psycopg; patch_psycopg(); del patch_psycopg

import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "exshare.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
