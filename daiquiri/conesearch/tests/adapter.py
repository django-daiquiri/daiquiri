from daiquiri.conesearch.adapter import BaseConeSearchAdapter


class BoxConeSearchAdapter(BaseConeSearchAdapter):
    sql_pattern = """
SELECT {columns}
FROM {schema}.{table}
WHERE {ra_column} BETWEEN {RA} - {SR} AND {RA} + {SR}
AND {dec_column} BETWEEN {DEC} - {SR} AND {DEC} + {SR}
"""

    def get_query_language(self, data):
        return 'postgresql'
