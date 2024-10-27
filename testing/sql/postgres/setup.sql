CREATE USER daiquiri_app WITH PASSWORD 'daiquiri_app';
CREATE USER daiquiri_data WITH PASSWORD 'daiquiri_data';

DROP DATABASE IF EXISTS test_daiquiri_app;
CREATE DATABASE test_daiquiri_app WITH OWNER daiquiri_app;

DROP DATABASE IF EXISTS test_daiquiri_data;
CREATE DATABASE test_daiquiri_data;

DROP DATABASE IF EXISTS test_daiquiri_tap;
CREATE DATABASE test_daiquiri_tap WITH OWNER daiquiri_data;

DROP DATABASE IF EXISTS test_daiquiri_oai;
CREATE DATABASE test_daiquiri_oai WITH OWNER daiquiri_data;

\c test_daiquiri_data;
\i testing/sql/postgres/archive.sql
\i testing/sql/postgres/obs.sql
\i testing/sql/postgres/sim.sql
\i testing/sql/postgres/test.sql
\i testing/sql/postgres/user.sql
