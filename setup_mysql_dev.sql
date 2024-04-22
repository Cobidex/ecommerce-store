-- Prepare a MySQL server for the development of the project
-- Usage: cat 'setup_mysql_dev' | sudo mysql;
CREATE DATABASE IF NOT EXISTS dev_db;
CREATE USER IF NOT EXISTS 'dev'@'localhost' IDENTIFIED BY 'dev_pwd';

GRANT ALL PRIVILEGES ON dev_db.* TO 'dev'@'localhost' WITH GRANT OPTION;
GRANT SELECT ON performance_schema.* TO 'dev'@'localhost';

