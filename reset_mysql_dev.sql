-- Reset a MySQL server for the development of the project
-- Usage: cat 'reset_mysql_dev' | sudo mysql;
DROP DATABASE IF EXISTS unmsa_dev_db;
CREATE DATABASE IF NOT EXISTS unmsa_dev_db;
CREATE USER IF NOT EXISTS 'dev'@'localhost' IDENTIFIED BY 'dev_pwd';

GRANT ALL PRIVILEGES ON unmsa_dev_db.* TO 'dev'@'localhost' WITH GRANT OPTION;
GRANT SELECT ON performance_schema.* TO 'dev'@'localhost';

