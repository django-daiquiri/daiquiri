DROP DATABASE IF EXISTS `daiquiri_data_test`;
CREATE DATABASE `daiquiri_data_test`;

CREATE TABLE `daiquiri_data_test`.`test` (
  `id` BIGINT primary key not null,
  `bool` TINYINT,
  `bigint` bigint,
  `double` double,
  `array` varchar(32),
  `matrix` varchar(32)
);

CREATE TABLE `daiquiri_data_test`.`datalink` (
  `datalink_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `ID` varchar(256) NOT NULL,
  `access_url` varchar(256),
  `service_def` varchar(80),
  `error_message` varchar(256),
  `description` varchar(256),
  `semantics` varchar(80) NOT NULL,
  `content_type` varchar(80),
  `content_length` int(11),
  PRIMARY KEY (`datalink_id`)
);

GRANT SELECT ON `daiquiri_data_test`.* TO 'daiquiri_data'@'localhost';

INSERT INTO daiquiri_data_test.test VALUES
(1, 1, 10, 10.0, '{1, 2, 3, 4, 5}', '{{1, 10}, {0, 0.1}}'),
(2, 1, 20, 20.0, '{2, 4, 6, 8, 10}', '{{2, 20}, {0, 0.2}}'),
(3, 0, 30, 30.0, '{3, 6, 9, 12, 15}', '{{3, 30}, {0, 0.3}}'),
(4, NULL, NULL, NULL, NULL, NULL);

INSERT INTO daiquiri_data_test.datalink
(`ID`, access_url, service_def, error_message, description, semantics, content_type, content_length) VALUES
('daiquiri_data_obs','http://example.com/docs/daiquiri_data_sim',NULL,NULL,'External documentation for schema daiquiri_data_obs','#auxiliary','text/html',NULL),
('daiquiri_data_obs','http://localhost:8000/files/dumps/daiquiri_data_sim.sql',NULL,NULL,'SQL dump of the schema','#this','application/sql',NULL);
