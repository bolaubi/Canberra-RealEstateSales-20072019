-- Queries to Create Database for "property_sales_canberra_preprocessed100.sql"
CREATE DATABASE property_sales_canberra_preprocessed100;
USE property_sales_canberra_preprocessed100;

-- Query to check all the inserted datas from "property_sales_canberra_preprocessed100.sql"
SELECT * FROM mytable;

-- Queries to show 10 latest inserted datas
SET @r = 0;
SELECT * FROM (SELECT *, (@r := @r + 1) AS r_id FROM property_sales_canberra_preprocessed100.mytable) AS tmp
    ORDER BY r_id DESC LIMIT 10;