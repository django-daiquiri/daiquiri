DROP SCHEMA IF EXISTS daiquiri_data_test CASCADE;
CREATE SCHEMA daiquiri_data_test;

CREATE TABLE "daiquiri_data_test"."test" (
  "id" bigint primary key not null,
  "bool" boolean,
  "bigint" bigint,
  "double" double precision,
  "array" double precision[3],
  "matrix" double precision[2][2]
);

GRANT USAGE ON SCHEMA daiquiri_data_test TO daiquiri_data;
GRANT SELECT ON ALL TABLES IN SCHEMA daiquiri_data_test TO daiquiri_data;

INSERT INTO daiquiri_data_test.test VALUES
(1, TRUE, 10, 10.0, '{1, 2, 3, 4, 5}', '{{1, 10}, {0, 0.1}}'),
(2, TRUE, 20, 20.0, '{2, 4, 6, 8, 10}', '{{2, 20}, {0, 0.2}}'),
(3, FALSE, 30, 30.0, '{3, 6, Nan, 12, 15}', '{{3, 30}, {0, 0.3}}'),
(4, NULL, NULL, NULL, NULL, NULL);
