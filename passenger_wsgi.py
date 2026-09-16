import os
import sys

PROJECT_ROOT = "/home/iwjzxhop/pichak-danesh"
VIRTUALENV_ROOT = "/home/iwjzxhop/virtualenv/pichak-danesh/3.12"

# CloudLinux Python Selector virtualenv uses both lib and lib64 site-packages.
# Passenger may start with a system Python, so explicitly expose the same
# virtualenv paths and project root before importing Django.
SITE_PACKAGES = [
    os.path.join(VIRTUALENV_ROOT, "lib64", "python3.12", "site-packages"),
    os.path.join(VIRTUALENV_ROOT, "lib", "python3.12", "site-packages"),
]

for path in SITE_PACKAGES:
    if path not in sys.path:
        sys.path.insert(0, path)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("VIRTUAL_ENV", VIRTUALENV_ROOT)
os.environ["PATH"] = os.path.join(VIRTUALENV_ROOT, "bin") + os.pathsep + os.environ.get("PATH", "")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
