import logging

from .adapter import DatalinkAdapter
from .models import Datalink

logger = logging.getLogger(__name__)


def update_links(resource_type, resource):
    logger.debug('update_links %s %s', resource_type, resource)

    adapter = DatalinkAdapter()

    try:
        identifier = adapter.get_identifier(resource_type, resource)
        links = adapter.get_links(resource_type, resource)
    except TypeError:
        raise RuntimeError('Could not obtain identifier or links for %s %s' % (resource_type, resource))

    datalinks = []
    for link in links:
        datalinks.append(Datalink(**link))

    Datalink.objects.filter(ID=identifier).delete()
    Datalink.objects.bulk_create(datalinks)


def delete_links(resource_type, resource):
    logger.debug('delete_links %s %s', resource_type, resource)

    adapter = DatalinkAdapter()

    try:
        identifier = adapter.get_identifier(resource_type, resource)
    except TypeError:
        raise RuntimeError('Could not obtain identifier for %s %s' % (resource_type, resource))

    Datalink.objects.filter(ID=identifier).delete()
