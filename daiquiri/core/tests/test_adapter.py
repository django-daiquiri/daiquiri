from daiquiri.core.adapter import DatabaseAdapter


def test_fetch_table(db):
    row = DatabaseAdapter().fetch_table('daiquiri_data_obs', 'stars')
    assert row['type'] == 'table'


def test_fetch_table_error(db):
    row = DatabaseAdapter().fetch_table('daiquiri_data_obs', 'stars1')
    assert row == {}


def test_fetch_row(db):
    row = DatabaseAdapter().fetch_row('daiquiri_data_obs', 'stars', column_names=None, search=None, filters={
        'id': '4551299946478123136'
    })
    assert row[0] == 4551299946478123136


def test_fetch_rows(db):
    rows = DatabaseAdapter().fetch_rows('daiquiri_data_obs', 'stars')
    assert len(rows) == 10
    assert len(rows[0]) == 4
    assert rows[0][0] == 1714709274237701248


def test_fetch_rows_filter(db):
    rows = DatabaseAdapter().fetch_rows('daiquiri_data_sim', 'halos', filters={
        'id': '85000000000'
    })
    assert len(rows) == 1
    assert len(rows[0]) == 8
    assert rows[0][0] == 85000000000


def test_fetch_nrows(db):
    nrows = DatabaseAdapter().fetch_nrows('daiquiri_data_obs', 'stars')
    assert nrows == 10000


def test_fetch_size(db):
    size = DatabaseAdapter().fetch_size('daiquiri_data_obs', 'stars')
    assert size > 0


def test_fetch_columns(db):
    columns = DatabaseAdapter().fetch_columns('daiquiri_data_obs', 'stars')
    assert len(columns) == 4
    assert columns[0]['indexed'] is True


def test_fetch_column(db):
    column = DatabaseAdapter().fetch_column('daiquiri_data_obs', 'stars', 'id')
    assert column['name'] == 'id'
    assert column['datatype']
    assert column['indexed'] is True


def test_fetch_column_names(db):
    columns = DatabaseAdapter().fetch_column_names('daiquiri_data_obs', 'stars')
    assert columns[0] == 'id'


def test_count_rows(db):
    row = DatabaseAdapter().count_rows('daiquiri_data_obs', 'stars')
    assert row == 10000
