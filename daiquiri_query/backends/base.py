class BaseQueryBackend(object):

    def submit(self, job):
        raise NotImplementedError()

    def get_user_db(self, username):
        raise NotImplementedError()
