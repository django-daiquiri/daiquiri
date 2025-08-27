CREATE SCHEMA daiquiri_data_test;

CREATE TABLE "daiquiri_data_test"."test" (
  "id" bigint primary key not null,
  "bool" boolean,
  "bigint" bigint,
  "double" double precision,
  "array" double precision[3],
  "matrix" double precision[2][2]
);

CREATE TABLE "daiquiri_data_test"."datalink" (
    datalink_id serial PRIMARY KEY,
    "ID" character varying(256) NOT NULL,
    access_url character varying(256),
    service_def character varying(80),
    error_message character varying(256),
    description character varying(256),
    semantics character varying(80) NOT NULL,
    content_type character varying(80),
    content_length integer
);

GRANT USAGE ON SCHEMA daiquiri_data_test TO daiquiri_data;
GRANT SELECT ON ALL TABLES IN SCHEMA daiquiri_data_test TO daiquiri_data;

INSERT INTO daiquiri_data_test.test VALUES
(1, TRUE, 10, 10.0, '{1, 2, 3, 4, 5}', '{{1, 10}, {0, 0.1}}'),
(2, TRUE, 20, 20.0, '{2, 4, 6, 8, 10}', '{{2, 20}, {0, 0.2}}'),
(3, FALSE, 30, 30.0, '{3, 6, Nan, 12, 15}', '{{3, 30}, {0, 0.3}}'),
(4, NULL, NULL, NULL, NULL, NULL);

INSERT INTO daiquiri_data_test.datalink
("ID", access_url, service_def, error_message, description, semantics, content_type, content_length) VALUES
('daiquiri_data_obs','http://example.com/docs/daiquiri_data_sim',NULL,NULL,'External documentation for schema daiquiri_data_obs','#auxiliary','text/html',NULL),
('daiquiri_data_obs','http://localhost:8000/files/dumps/daiquiri_data_sim.sql',NULL,NULL,'SQL dump of the schema','#this','application/sql',NULL);
