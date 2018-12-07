from django.utils.translation import ugettext_lazy as _

LICENSE_CC0 = 'CC0'
LICENSE_PD = 'PD'
LICENSE_BY = 'BY'
LICENSE_BY_SA = 'BY_SA'
LICENSE_BY_ND = 'BY_ND'
LICENSE_BY_NC = 'BY_NC'
LICENSE_BY_NC_SA = 'BY_NC_SA'
LICENSE_BY_NC_ND = 'BY_NC_ND'
LICENSE_CHOICES = (
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

ACCESS_LEVEL_PRIVATE = 'PRIVATE'
ACCESS_LEVEL_INTERNAL = 'INTERNAL'
ACCESS_LEVEL_PUBLIC = 'PUBLIC'
ACCESS_LEVEL_CHOICES = (
    (ACCESS_LEVEL_PRIVATE, _('Private - access must be granted by group')),
    (ACCESS_LEVEL_INTERNAL, _('Internal - logged in users can access')),
    (ACCESS_LEVEL_PUBLIC, _('Public - anonymous visitors can access'))
)

GROUPS = {
    'wordpress_editor': [],
    'wordpress_admin': [],
    'contact_manager': [
        'daiquiri_contact.view_contactmessage',
        'daiquiri_contact.add_contactmessage',
        'daiquiri_contact.change_contactmessage',
        'daiquiri_contact.delete_contactmessage'
    ],
    'meetings_manager': [
        'daiquiri_meetings.view_meeting',
        'daiquiri_meetings.add_meeting',
        'daiquiri_meetings.change_meeting',
        'daiquiri_meetings.delete_meeting',
        'daiquiri_meetings.view_participant',
        'daiquiri_meetings.add_participant',
        'daiquiri_meetings.change_participant',
        'daiquiri_meetings.delete_participant',
        'daiquiri_meetings.view_contribution',
        'daiquiri_meetings.add_contribution',
        'daiquiri_meetings.change_contribution',
        'daiquiri_meetings.delete_contribution'
    ],
    'metadata_manager': [
        'daiquiri_metadata.view_schema',
        'daiquiri_metadata.add_schema',
        'daiquiri_metadata.change_schema',
        'daiquiri_metadata.delete_schema',
        'daiquiri_metadata.view_table',
        'daiquiri_metadata.add_table',
        'daiquiri_metadata.change_table',
        'daiquiri_metadata.delete_table',
        'daiquiri_metadata.view_column',
        'daiquiri_metadata.add_column',
        'daiquiri_metadata.change_column',
        'daiquiri_metadata.delete_column',
        'daiquiri_metadata.view_function',
        'daiquiri_metadata.add_function',
        'daiquiri_metadata.change_function',
        'daiquiri_metadata.delete_function'
    ],
    'stats_manager': [
        'daiquiri_stats.view_record'
    ],
    'query_manager': [
        'daiquiri_query.view_example',
        'daiquiri_query.add_example',
        'daiquiri_query.change_example',
        'daiquiri_query.delete_example'
    ],
    'user_manager': [
        'daiquiri_auth.view_profile',
        'daiquiri_auth.change_profile'
    ]
}
