# Configure one DataLink service per result column that has its own ID family.
DATALINK_SERVICES = [
    {
        'column_name': None,
        'path': '/',
        'adapter': 'daiquiri.datalink.adapter.DefaultDatalinkAdapter',
    }
]
DATALINK_ADAPTER = None  # Deprecated: overrides the root adapter in DATALINK_SERVICES.
DATALINK_TABLES = []
DATALINK_CUSTOM_SEMANTICS = {
    "#doi": "The access_url points to the Digital Object Identifier (DOI) of the object.",
}
