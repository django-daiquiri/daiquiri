class DaiquiriRouter(object):

    def db_for_read(self, model, **hints):
        if model._meta.app_label == self.label:
            return self.db
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == self.label:
            return self.db
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == self.db or \
           obj2._meta.app_label == self.db:

            return True

        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == self.db:
            if app_label == self.label:
                return True
            else:
                return False
        else:
            if app_label == self.label:
                return False
            else:
                # pass on to the next router
                return None


class DataRouter(object):

    def db_for_read(self, model, **hints):
        return None

    def db_for_write(self, model, **hints):
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == 'data':
            return False
        return None
