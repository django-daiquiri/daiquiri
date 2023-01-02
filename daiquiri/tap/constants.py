TAP_SCHEMA_METADATA = {
    'order': 1000,
    'description': 'The TAP SCHEMA of the service',
    'access_level': 'PUBLIC',
    'metadata_access_level': 'PUBLIC',
    'tables': [
        {
            'name': 'schemas',
            'description': 'The table of schemas for the service',
            'order': 1,
            'access_level': 'PUBLIC',
            'metadata_access_level': 'PUBLIC',
            'columns': [
                {
                    'name': 'id',
                    'description': 'Internal ID of the schema',
                    'order': 1,
                    'datatype': 'integer',
                    'arraysize': None,
                    'std': False,
                    'access_level': 'PUBLIC',
                    'metadata_access_level': 'PUBLIC'
                },
                {
                    'name': 'schema_name',
                    'description': 'The name of the schema',
                    'order': 2,
                    'datatype': 'char',
                    'arraysize': 256,
                    'std': True,
                    'access_level': 'PUBLIC',
                    'metadata_access_level': 'PUBLIC'
                },
                {
                    'name': 'utype',
                    'description': 'The IVOA UTYPE of the schema',
                    'order': 3,
                    'datatype': 'char',
                    'arraysize': 256,
                    'std': True,
                    'access_level': 'PUBLIC',
                    'metadata_access_level': 'PUBLIC'
                },
                {
                    'name': 'description',
                    'description': 'The description of the schema',
                    'order': 4,
                    'datatype': 'char',
                    'arraysize': 256,
                    'std': True,
                    'access_level': 'PUBLIC',
                    'metadata_access_level': 'PUBLIC'
                }
            ]
        },
        {
            'name': 'tables',
            'description': 'The table of tables for the service',
            'order': 2,
            'access_level': 'PUBLIC',
            'metadata_access_level': 'PUBLIC',
            'columns': [
                {
                    'name': 'id',
                    'description': 'Internal ID of the table',
                    'order': 1,
                    'datatype': 'integer',
                    'arraysize': None,
                    'std': False,
                    'access_level': 'PUBLIC',
                    'metadata_access_level': 'PUBLIC'
                },
                {
                    'name': 'schema_name',
                    'description': 'The name of the schema of the table',
                    'order': 2,
                    'datatype': 'char',
                    'arraysize': 256,
                    'std': True,
                    'access_level': 'PUBLIC',
                    'metadata_access_level': 'PUBLIC'
                },
                {
                    'name': 'table_name',
                    'description': 'The name of the table',
                    'order': 3,
                    'datatype': 'char',
                    'arraysize': 256,
                    'std': True,
                    'access_level': 'PUBLIC',
                    'metadata_access_level': 'PUBLIC'
                },
                {
                    'name': 'table_type',
                    'description': 'The type of the table (table or view)',
                    'order': 4,
                    'datatype': 'char',
                    'arraysize': 256,
                    'std': True,
                    'access_level': 'PUBLIC',
                    'metadata_access_level': 'PUBLIC'
                },
                {
                    'name': 'utype',
                    'description': 'The IVOA UTYPE of the table',
                    'order': 5,
                    'datatype': 'char',
                    'arraysize': 256,
                    'std': True,
                    'access_level': 'PUBLIC',
                    'metadata_access_level': 'PUBLIC'
                },
                {
                    'name': 'description',
                    'description': 'The description of the table',
                    'order': 6,
                    'datatype': 'char',
                    'arraysize': 256,
                    'std': True,
                    'access_level': 'PUBLIC',
                    'metadata_access_level': 'PUBLIC'
                },
                {
                    'name': 'table_index',
                    'description': 'The ordering index of the table',
                    'order': 7,
                    'datatype': 'integer',
                    'arraysize': None,
                    'std': True,
                    'access_level': 'PUBLIC',
                    'metadata_access_level': 'PUBLIC'
                },
                {
                    'name': 'schema_id',
                    'description': 'The foreign key to the schema of this table',
                    'order': 8,
                    'datatype': 'integer',
                    'arraysize': None,
                    'std': False,
                    'access_level': 'PUBLIC',
                    'metadata_access_level': 'PUBLIC'
                }
            ]
        },
        {
            'name': 'columns',
            'description': 'The table of columns of the service',
            'order': 3,
            'access_level': 'PUBLIC',
            'metadata_access_level': 'PUBLIC',
            'columns': [
                {
                    'name': 'id',
                    'description': 'Internal ID of the column',
                    'order': 1,
                    'datatype': 'integer',
                    'arraysize': None,
                    'std': True,
                    'access_level': 'PUBLIC',
                    'metadata_access_level': 'PUBLIC'
                },
                {
                    'name': 'table_name',
                    'description': 'The name of the table of the column',
                    'order': 2,
                    'datatype': 'char',
                    'arraysize': 256,
                    'std': True,
                    'access_level': 'PUBLIC',
                    'metadata_access_level': 'PUBLIC'
                },
                {
                    'name': 'column_name',
                    'description': 'The name of the column',
                    'order': 3,
                    'datatype': 'char',
                    'arraysize': 256,
                    'std': True,
                    'access_level': 'PUBLIC',
                    'metadata_access_level': 'PUBLIC'
                },
                {
                    'name': 'datatype',
                    'description': 'The datatype of the column',
                    'order': 4,
                    'datatype': 'char',
                    'arraysize': 256,
                    'std': True,
                    'access_level': 'PUBLIC',
                    'metadata_access_level': 'PUBLIC'
                },
                {
                    'name': 'arraysize',
                    'description': 'The size of the column for variable length datatypes',
                    'order': 5,
                    'datatype': 'integer',
                    'arraysize': None,
                    'std': True,
                    'access_level': 'PUBLIC',
                    'metadata_access_level': 'PUBLIC'
                },
                {
                    'name': 'size',
                    'description': 'The size of the column for variable length datatypes (legacy)',
                    'order': 6,
                    'datatype': 'integer',
                    'arraysize': None,
                    'std': True,
                    'access_level': 'PUBLIC',
                    'metadata_access_level': 'PUBLIC'
                },
                {
                    'name': 'description',
                    'description': 'The description of the column',
                    'order': 7,
                    'datatype': 'char',
                    'arraysize': 256,
                    'std': True,
                    'access_level': 'PUBLIC',
                    'metadata_access_level': 'PUBLIC'
                },
                {
                    'name': 'utype',
                    'description': 'The IVOA UTYPE of the column',
                    'order': 8,
                    'datatype': 'char',
                    'arraysize': 256,
                    'std': True,
                    'access_level': 'PUBLIC',
                    'metadata_access_level': 'PUBLIC'
                },
                {
                    'name': 'unit',
                    'description': 'The Unit of the column',
                    'order': 9,
                    'datatype': 'char',
                    'arraysize': 256,
                    'std': True,
                    'access_level': 'PUBLIC',
                    'metadata_access_level': 'PUBLIC'
                },
                {
                    'name': 'ucd',
                    'description': 'The IVOA UCD of the column',
                    'order': 10,
                    'datatype': 'char',
                    'arraysize': 256,
                    'std': True,
                    'access_level': 'PUBLIC',
                    'metadata_access_level': 'PUBLIC'
                },
                {
                    'name': 'principal',
                    'description': 'Designates if the column is considered a core part of the service',
                    'order': 11,
                    'datatype': 'boolean',
                    'arraysize': None,
                    'std': True,
                    'access_level': 'PUBLIC',
                    'metadata_access_level': 'PUBLIC'
                },
                {
                    'name': 'indexed',
                    'description': 'Designates if the column is indexed',
                    'order': 12,
                    'datatype': 'boolean',
                    'arraysize': None,
                    'std': True,
                    'access_level': 'PUBLIC',
                    'metadata_access_level': 'PUBLIC'
                },
                {
                    'name': 'std',
                    'description': 'Designates if the column is defined by some standard',
                    'order': 13,
                    'datatype': 'boolean',
                    'arraysize': None,
                    'std': True,
                    'access_level': 'PUBLIC',
                    'metadata_access_level': 'PUBLIC'
                },
                {
                    'name': 'column_index',
                    'description': 'The ordering index of the column',
                    'order': 14,
                    'datatype': 'integer',
                    'arraysize': None,
                    'std': True,
                    'access_level': 'PUBLIC',
                    'metadata_access_level': 'PUBLIC'
                },
                {
                    'name': 'table_id',
                    'description': 'The foreign key to the table of this column',
                    'order': 15,
                    'datatype': 'integer',
                    'arraysize': None,
                    'std': False,
                    'access_level': 'PUBLIC',
                    'metadata_access_level': 'PUBLIC'
                }
            ]
        }
    ]
}
