"""Presentation of pgSphere values; database values and queries remain native."""

import math
import re

from daiquiri.core.utils import is_adql

PGSPHERE_TYPES = {
    'spoint',
    'scircle',
    'sbox',
    'spoly',
    'sline',
    'sellipse',
    'spath',
    'strans',
    'smoc',
}
ADQL_GEOMETRIES = {
    'spoint': ('point', 2),
    'scircle': ('circle', 3),
    'sbox': ('box', 4),
    'spoly': ('polygon', '*'),
}

_NUMBER = r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?'


def convert_geometry_to_adql(value, datatype):
    """Decode pgSphere text in radians into a flat list of angles in degrees."""
    if value is None or value == 'NULL' or (isinstance(value, float) and math.isnan(value)):
        return None
    if not isinstance(value, str):
        raise ValueError(f'Invalid pgSphere {datatype} result: {value!r}')
    angles = [math.degrees(float(angle)) for angle in re.findall(_NUMBER, value)]
    if not all(math.isfinite(angle) for angle in angles):
        raise ValueError(f'Non-finite pgSphere {datatype} result: {value!r}')
    if datatype == 'sbox':
        west, south, east, north = angles
        width = (east - west) % 360
        # Equal longitudes enclose the full range unless the box is a point.
        if width == 0 and (north != south or east != west):
            width = 360.0
        return [(west + width / 2) % 360, (south + north) / 2, width, north - south]
    return angles


def process_result_columns(columns, query_language):
    """Return presentation metadata without modifying the stored metadata."""
    if not is_adql(query_language):
        return columns
    result = []
    for column in columns:
        geometry = ADQL_GEOMETRIES.get(column.get('datatype'))
        if geometry:
            xtype, arraysize = geometry
            column = dict(column, datatype='double[]', arraysize=arraysize, unit='deg', xtype=xtype)
        result.append(column)
    return result


def process_result_row(row, columns, query_language):
    """Convert only typed geometry cells of an ADQL result."""
    if not is_adql(query_language):
        return row
    return [
        convert_geometry_to_adql(value, column['datatype'])
        if column.get('datatype') in ADQL_GEOMETRIES
        else value
        for value, column in zip(row, columns, strict=True)
    ]
