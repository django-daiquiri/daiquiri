class BaseQueryBackend(object):

    def submit(self, job):
        raise NotImplementedError()
