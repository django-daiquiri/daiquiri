import os
import logging
from os.path import isfile
from distributed import Client
from queryparser.postgresql import PostgreSQLQueryProcessor

logger = logging.getLogger(__name__)


class DaskSQLAdapter(object):

    DATATYPES = {
        'int16': {
            'datatype': 'short',
            'arraysize': False,
        },
        'int32': {
            'datatype': 'int',
            'arraysize': False,
        },
        'int64': {
            'datatype': 'long',
            'arraysize': False,
        },
        'float32': {
            'datatype': 'float',
            'arraysize': False,
        },
        'float64': {
            'datatype': 'double',
            'arraysize': False,
        },
        'string': {
            'datatype': 'char',
            'arraysize': False,
        },
        'bool': {
            'datatype': 'boolean',
            'arraysize': False,
        },
    }

    def __init__(self, key, db):
        host = db['HOST']
        port = db['PORT']
        self.data_path = db['NAME']
        self.client = Client(f"{host}:{port}")
        self.database_config = db


    def fetch_tables(self, schema_name):
        def _discover_tables(path_to_files: str) -> list[str]:
            import os
            tables = []
            table_path = os.path.join(path_to_files, schema_name)
            table_names = os.listdir(table_path)
            table_names = [t.split('.')[0] for t in table_names]
            # tables.append([f'{t}' for t in table_names])
            return table_names

        future = self.client.submit(_discover_tables, self.data_path)
        table_names = future.result() # [0]
        return [{ 'name': t, 'type': 'table'} for t in table_names]


    def fetch_columns(self, schema_name, table_name):
        def _discover_columns(path_to_table):
            import dask.dataframe as dd
            df = dd.read_parquet(path_to_table, engine='pyarrow')
            columns = []
            for order, col in enumerate(df.columns):
                column = {
                    'name': col,
                    'order': order+1,
                    'datatype': str(df.dtypes[col]),
                    'arraysize': None,
                }
                columns.append(column)
            return columns

        path_to_table = os.path.join(self.data_path, schema_name, table_name)
        result = self.client.submit(_discover_columns, path_to_table)
        columns = result.result()
        for i, col in enumerate(columns):
            if col['datatype'] in self.DATATYPES:
                columns[i]['datatype'] = self.DATATYPES[col['datatype']]['datatype']
            else:
                columns[i]['datatype'] = None
        return columns

    def create_user_schema_if_not_exists(self, schema_name):
        def _create_schema(path_to_schema):
            import os
            if not os.path.exists(path_to_schema):
                os.mkdir(path_to_schema)

        path_to_schema = os.path.join(self.data_path, schema_name)
        self.client.submit(_create_schema, path_to_schema)

    def fetch_pid(self):
        return None

    def build_query(self, schema_name, table_name, native_query, timeout=None, max_records=None):
        return f"create table {schema_name}.{table_name} as {native_query};"

    def submit_query(self, query: str):
        native_query = query.lower()
        created_table = None
        if native_query.startswith("create table"):
            prefix = native_query.split(" as ")[0]
            created_table = prefix.removeprefix("create table ").strip()
            prefix += " as "
            native_query = native_query.removeprefix(prefix)
        print(native_query)
        qp = PostgreSQLQueryProcessor(native_query)
        qp.process_query()
        query_tables = [f"{t[0]}.{t[1]}" for t in qp.tables]

        def _execute_dask_sql(query, data_path, tables, created_table):
            from dask_sql import Context
            import dask.dataframe as dd
            import os
            c = Context()
            schemas = set()
            for table in tables:
                schema_name = table.split(".")[0]
                table_name = table.split(".")[1]
                if schema_name not in schemas:
                    schemas.add(schema_name)
                    c.create_schema(schema_name)
                path_to_table = os.path.join(data_path, schema_name, f"{table_name}")
                ddf = dd.read_parquet(path_to_table)
                c.create_table(table_name, ddf, schema_name=schema_name)

            if created_table:
                schema_name = created_table.split(".")[0]
                if schema_name not in schemas:
                    c.create_schema(schema_name)

            result = c.sql(query)
            if created_table:
                schema_name = created_table.split(".")[0]
                table_name = created_table.split(".")[1]
                path_to_created_table = os.path.join(data_path, schema_name, f"{table_name}")
                # os.mkdir(path_to_created_table)
                df = dd.from_pandas(c.schema[schema_name].tables[table_name].df.compute(), chunksize=500000)
                name_function = lambda x: f"part{x}.parquet"
                df.to_parquet(os.path.join(path_to_created_table, ""), engine='pyarrow', name_function=name_function)
                return df

            return result.compute()

        res = self.client.submit(_execute_dask_sql, query, self.data_path, query_tables, created_table)
        return res.result()


    def count_rows(self, schema_name, table_name, column_names=None, search=None, filters=None):
        def _count_rows(path_to_table):
            import dask.dataframe as dd
            df = dd.read_parquet(path_to_table, engine='pyarrow')
            return df.shape[0].compute()

        path_to_table = os.path.join(self.data_path, schema_name, table_name)
        result = self.client.submit(_count_rows, path_to_table)
        nrows = result.result()
        return nrows

    def fetch_rows(self, schema_name, table_name,
                   column_names=None,
                   ordering=None,
                   page=1,
                   page_size=10,
                   search=None,
                   filters=None):

        def _execute_dask_sql(schema_name, table_name, data_path, query):
            import os
            from dask_sql import Context
            import dask.dataframe as dd
            c = Context()
            path_to_table = os.path.join(data_path, schema_name, table_name)
            df = dd.read_parquet(path_to_table, engine='pyarrow')
            c.create_schema(schema_name)
            c.create_table(table_name, df, schema_name=schema_name)
            result = c.sql(query).compute()
            return result

        if not column_names:
            column_names = ["*",]

        query = f"select {','.join(column_names)} from {schema_name}.{table_name}"
        if page_size > 0:
            offset = (int(page) - 1) * int(page_size)
            query += f" LIMIT {page_size} OFFSET {offset}"
        query += ";"
        result = self.client.submit(_execute_dask_sql, schema_name, table_name, self.data_path, query).result()
        return tuple(result.itertuples(index=False, name=None))



    def fetch_size(self, schema_name, table_name):
        def _fetch_size(path_to_table):
            def get_dir_size(path_to_table):
                total = 0
                with os.scandir(path_to_table) as it:
                    for entry in it:
                        if entry.is_file():
                            total += entry.stat().st_size
                        elif entry.is_dir():
                            total += get_dir_size(entry.path)
                return total
            return get_dir_size(path_to_table)

        path_to_table = os.path.join(self.data_path, schema_name, table_name)
        result = self.client.submit(_fetch_size, path_to_table)
        size = result.result()
        return size

    def drop_table(self, schema_name, table_name):
        def _rm_parquet_file(path_to_table):
            import os
            import shutil
            if os.path.isfile(path_to_table):
                os.remove(path_to_table)
            elif os.path.isdir(path_to_table):
                shutil.rmtree(path_to_table)

        path_to_table = os.path.join(self.data_path, schema_name, table_name)
        self.client.submit(_rm_parquet_file, path_to_table)

    def abort_query(self, pid):
        pass
