# include settimgs from daiquiri
from daiquiri.core.settings.django import *
from daiquiri.core.settings.daiquiri import *
from daiquiri.core.settings.logging import *
from daiquiri.core.settings.vendor import *

from daiquiri.auth.settings import *
from daiquiri.conesearch.settings import *
from daiquiri.contact.settings import *
from daiquiri.cutout.settings import *
from daiquiri.datalink.settings import *
from daiquiri.files.settings import *
from daiquiri.metadata.settings import *
from daiquiri.oai.settings import *
from daiquiri.query.settings import *
from daiquiri.registry.settings import *
from daiquiri.serve.settings import *
from daiquiri.stats.settings import *
from daiquiri.tap.settings import *

# override settings from base.py (which is checked in to git)
try:
    from .base import *
except ImportError:
    pass

# override settings from local.py (which is not checked in to git)
try:
    from .local import *
except ImportError:
    pass
