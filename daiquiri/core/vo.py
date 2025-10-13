from django.conf import settings


def get_curation():
    return {
        'publisher': settings.SITE_PUBLISHER,
        'publisher_properites': settings.SITE_PUBLISHER_PROPERTIES,
        'date': settings.SITE_UPDATED,
        'creator': {
            'name': settings.SITE_CREATOR,
            'logo': settings.SITE_LOGO_URL,
        },
        'contact': settings.SITE_CONTACT
    }
