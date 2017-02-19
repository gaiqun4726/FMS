import django

from fpms.modules.loader import *

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FMS.settings")
django.setup()
# print ResLoader.getRootPath()
fdg = InitialFDLoader()
fdg.getInitialFD()