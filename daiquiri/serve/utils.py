import os

from daiquiri.query.utils import get_user_database_name

from daiquiri.metadata.models import Database, Table, Column
from daiquiri.query.models import QueryJob


def get_columns(user, database_name, table_name):

    user_database_name = get_user_database_name(user)

    if database_name == user_database_name:
        # get the job fetch the columns
        job = QueryJob.objects.filter_by_owner(user).exclude(phase=QueryJob.PHASE_ARCHIVED).get(
            database_name=database_name,
            table_name=table_name
        )

        return job.metadata['columns']

    else:
        # check permissions on the database
        database = Database.objects.filter_by_access_level(user).get(name=database_name)

        # check permissions on the table
        table = Table.objects.filter_by_access_level(user).filter(database=database).get(name=table_name)

        # get columns for this table
        return Column.objects.filter_by_access_level(user).filter(table=table).values()


def get_full_path(directory_path, file_path):

    directory_path_tokens = directory_path.rstrip('/').split('/')
    file_path_tokens = file_path.lstrip('/').split('/')

    match = 0
    for i in range(len(file_path_tokens)):
        if file_path_tokens[:i] == directory_path_tokens[-i:]:
            match = i

    return os.path.join(directory_path, *file_path_tokens[match:])
