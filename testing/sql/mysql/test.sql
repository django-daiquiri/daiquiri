CREATE USER IF NOT EXISTS 'daiquiri_app'@'localhost' identified by 'daiquiri_app';
CREATE USER IF NOT EXISTS 'daiquiri_data'@'localhost' identified by 'daiquiri_data';

DROP DATABASE IF EXISTS `test_daiquiri_app`;
CREATE DATABASE `test_daiquiri_app` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON `test_daiquiri_app`.* to 'daiquiri_app'@'localhost';

DROP DATABASE IF EXISTS `test_daiquiri_data`;
CREATE DATABASE `test_daiquiri_data` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON `test_daiquiri_data`.* to 'daiquiri_data'@'localhost';

DROP DATABASE IF EXISTS `test_tap_schema`;
CREATE DATABASE `test_tap_schema` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON `test_tap_schema`.* to 'daiquiri_data'@'localhost';

DROP DATABASE IF EXISTS `test_oai_schema`;
CREATE DATABASE `test_oai_schema` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON `test_oai_schema`.* to 'daiquiri_data'@'localhost';
