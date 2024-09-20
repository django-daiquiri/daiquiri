import os
from distributed import Client
from daiquiri.core.adapter.download.base import BaseDownloadAdapter


class DaskDownloadAdapter(BaseDownloadAdapter):

    def set_args(self, schema_name, table_name, data_only=False):
        host = self.database_config['HOST']
        port = self.database_config['PORT']
        self.client = Client(f"{host}:{port}")
        self.schema_name = schema_name
        self.table_name = table_name
        self.data_path = self.database_config['NAME']

    def generate_rows(self, prepend=None):
        def _get_table(path_to_table):
            import dask.dataframe as dd
            df = dd.read_parquet(path_to_table, engine='pyarrow').compute()
            return df
        path_to_table = os.path.join(self.data_path, self.schema_name, self.table_name)
        df = self.client.submit(_get_table, path_to_table).result()
        df.reset_index()
        for _, row in df.iterrows():
            yield row.tolist()
