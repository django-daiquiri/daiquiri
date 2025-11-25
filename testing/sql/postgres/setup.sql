CREATE USER daiquiri_app WITH PASSWORD 'daiquiri_app';
CREATE USER daiquiri_data WITH PASSWORD 'daiquiri_data';

CREATE DATABASE test_daiquiri_app WITH OWNER daiquiri_app;

CREATE DATABASE test_daiquiri_data;

CREATE DATABASE test_daiquiri_tap WITH OWNER daiquiri_data;

CREATE DATABASE test_daiquiri_oai WITH OWNER daiquiri_data;

\c test_daiquiri_data;
\i testing/sql/postgres/data/archive.sql
\i testing/sql/postgres/data/obs.sql
\i testing/sql/postgres/data/sim.sql
\i testing/sql/postgres/data/test.sql
\i testing/sql/postgres/data/user.sql
