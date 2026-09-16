import os
import sys

PROJECT_ROOT = "/home/iwjzxhop/pichak-danesh"
VIRTUALENV_ROOT = "/home/iwjzxhop/virtualenv/pichak-danesh/3.12"
SITE_PACKAGES = os.path.join(VIRTUALENV_ROOT, "lib", "python3.12", "site-packages")

# Passenger may start the app with its own Python interpreter. Explicitly add
# the project's virtualenv packages so Django and the installed dependencies
# are available to the WSGI process.
if SITE_PACKAGES not in sys.path:
    sys.path.insert(0, SITE_PACKAGES)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
