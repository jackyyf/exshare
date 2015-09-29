"""
WSGI config for exshare project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

from gevent import monkey; monkey.patch_all(); del monkey
from psycogreen.gevent import patch_psycopg; patch_psycopg(); del patch_psycopg

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "exshare.settings")

application = get_wsgi_application()
