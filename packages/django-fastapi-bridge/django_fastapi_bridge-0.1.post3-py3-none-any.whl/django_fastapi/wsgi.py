import os
import sys

import django

from .registry import get_default_api

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webapi_prj.settings")

django.setup(set_prefix=False)
api = get_default_api()
