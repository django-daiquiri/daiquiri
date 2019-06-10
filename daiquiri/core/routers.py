# see also https://strongarm.io/blog/multiple-databases-in-django/

class DaiquiriRouter(object):

    def db_for_read(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return self.db
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return self.db
        return None

    def allow_relation(self, obj1, obj2, **hints):
        # Allow any relation between two models that are both in the `app_label` app.
        if obj1._meta.app_label == self.app_label or obj2._meta.app_label == self.app_label:
            return True

        # No opinion if neither object is in the Example app (defer to default or other routers).
        elif self.app_label not in [obj1._meta.app_label, obj2._meta.app_label]:
            return None

        # Block relationship if one object is in the `app_label` and the other isn't.
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == self.app_label:
            # The `app_label` should be migrated only on the `db` database.
            return db == self.db

        elif db == self.db:
            # Ensure that all other apps don't get migrated on the example_db database.
            return False

        # No opinion for all other scenarios
        return None


class DataRouter(object):

    def db_for_read(self, model, **hints):
        return None

    def db_for_write(self, model, **hints):
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # prevent migrations for the `data` db
        if db == 'data':
            return False
        return None
