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

GRANT SELECT ON `daiquiri_data_test`.* TO 'daiquiri_data'@'localhost';

INSERT INTO daiquiri_data_test.test VALUES
(1, 1, 10, 10.0, '{1, 2, 3, 4, 5}', '{{1, 10}, {0, 0.1}}'),
(2, 1, 20, 20.0, '{2, 4, 6, 8, 10}', '{{2, 20}, {0, 0.2}}'),
(3, 0, 30, 30.0, '{3, 6, 9, 12, 15}', '{{3, 30}, {0, 0.3}}'),
(4, NULL, NULL, NULL, NULL, NULL);
