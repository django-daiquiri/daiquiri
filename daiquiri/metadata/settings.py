from django.utils.translation import gettext_lazy as _

import daiquiri.core.env as env

METADATA_COLUMN_PERMISSIONS = False
METADATA_BASE_URL = None

# This setting sets the default width of the columns in the results of
# query and in the 'serve' app. If the column is not found here, then
# default is used. The key for the specific column is of the form
# 'schema_name.table_name.column_name'
METADATA_COLUMN_WIDTH = {
    'default': 200,
}

ARCHIVE_BASE_PATH = env.get_abspath('ARCHIVE_BASE_PATH')

LICENSE_NONE = ''
LICENSE_CC0 = 'CC0'
LICENSE_PD = 'PD'
LICENSE_BY = 'BY'
LICENSE_BY_SA = 'BY_SA'
LICENSE_BY_ND = 'BY_ND'
LICENSE_BY_NC = 'BY_NC'
LICENSE_BY_NC_SA = 'BY_NC_SA'
LICENSE_BY_NC_ND = 'BY_NC_ND'

LICENSE_CHOICES = (
    (LICENSE_NONE, _('---')),
    (LICENSE_CC0, _('CC0 1.0 Universal (CC0 1.0)')),
    (LICENSE_PD, _('Public Domain Mark')),
    (LICENSE_BY, _('Attribution 4.0 International (CC BY 4.0)')),
    (LICENSE_BY_SA, _('Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)')),
    (LICENSE_BY_ND, _('Attribution-NoDerivatives 4.0 International (CC BY-ND 4.0)')),
    (LICENSE_BY_NC, _('Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)')),
    (LICENSE_BY_NC_SA, _('Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)')),
    (LICENSE_BY_NC_ND, _('Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0)'))
)

LICENSE_URLS = {
    LICENSE_CC0: 'https://creativecommons.org/publicdomain/zero/1.0/',
    LICENSE_PD: None,
    LICENSE_BY: 'https://creativecommons.org/licenses/by/4.0/',
    LICENSE_BY_SA: 'https://creativecommons.org/licenses/by-sa/4.0/',
    LICENSE_BY_ND: 'https://creativecommons.org/licenses/by-nd/4.0/',
    LICENSE_BY_NC: 'https://creativecommons.org/licenses/by-nc/4.0/',
    LICENSE_BY_NC_SA: 'https://creativecommons.org/licenses/by-nc-sa/4.0/',
    LICENSE_BY_NC_ND: 'https://creativecommons.org/licenses/by-nc-nd/4.0/'
}

LICENSE_IDENTIFIERS = {
    LICENSE_CC0: 'CC0-1.0',
    LICENSE_PD: None,
    LICENSE_BY: 'CC-BY-4.0',
    LICENSE_BY_SA: 'CC-BY-SA-4.0',
    LICENSE_BY_ND: 'CC-BY-ND-4.0',
    LICENSE_BY_NC: 'CC-BY-NC-4.0',
    LICENSE_BY_NC_SA: 'CC-BY-NC-SA-4.0',
    LICENSE_BY_NC_ND: 'CC-BY-NC-ND-4.0'
}
