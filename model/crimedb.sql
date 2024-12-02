CREATE DATABASE CrimeDB;

CREATE TABLE Users (id INT AUTO_INCREMENT PRIMARY KEY,\
                        fullname VARCHAR(50),\
                        username VARCHAR(32) NOT NULL,\
                        password VARCHAR(128) NOT NULL, \
                        email VARCHAR(50),\
                        phone VARCHAR(50), \
                        address VARCHAR(128)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Crime ( X DOUBLE,\
                    Y DOUBLE,\
                    event_unique_id VARCHAR(255),\
                    occurrencedate VARCHAR(255),\
                    reporteddate VARCHAR(255),\
                    premisetype VARCHAR(255),\
                    ucr_code INT,\
                    ucr_ext INT,\
                    offence VARCHAR(255),\
                    reportedyear YEAR,\
                    reportedmonth VARCHAR(255),\
                    reportedday INT,\
                    reporteddayofyear INT,\
                    reporteddayofweek VARCHAR(255),\
                    reportedhour INT,\
                    MCI VARCHAR(255),\
                    Division CHAR(255),\
                    Hood_ID INT,\
                    Neighbourhood VARCHAR(255),\
                    Longitude DOUBLE,\
                    Latitude DOUBLE,\
                    occurrencedayofyear INT,\
                    occurrencedayofweek  VARCHAR(255),\
                    occurrencehour INT,\
                    occurrenceday INT,\
                    occurrencemonth VARCHAR(255),\
                    occurrenceyear YEAR ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;