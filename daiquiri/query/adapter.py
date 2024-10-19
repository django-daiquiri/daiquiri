class QueryFormAdapter:

    def get_fields(self):
        raise NotImplementedError

    def get_query_language(self, data):
        raise NotImplementedError

    def get_query(self, data):
        raise NotImplementedError
