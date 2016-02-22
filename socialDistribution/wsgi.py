"""
WSGI config for socialDistribution project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""


import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "socialDistribution.settings")

from django.core.wsgi import get_wsgi_application

from whitenoise.django import DjangoWhiteNoise

'''
dj-static allows you to properly serve static assets 
from production with a WSGI server: https://pypi.python.org/pypi/dj-static
''' 
from dj_static import Cling
application = Cling(get_wsgi_application())
application = DjangoWhiteNoise(application)
