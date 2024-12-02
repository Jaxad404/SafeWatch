import mysql.connector
# from conf import dbConfig, userConfig, adminConfig
import time
# from concurrent.futures import ThreadPoolExecutor


class DTB:
    def __init__(self, dbconf):
        self.dbconf = dbconf
        self.dtb = mysql.connector.connect(**self.dbconf)
        self.db_time = time.ctime()

    def createUsersTable(self):
        cursor = self.dtb.cursor()
        cursor.execute("CREATE TABLE Users (id INT AUTO_INCREMENT PRIMARY KEY,\
                        fullname VARCHAR(50),\
                        username VARCHAR(32) NOT NULL,\
                        password VARCHAR(128) NOT NULL, \
                        email VARCHAR(50),\
                        phone VARCHAR(50), \
                        address VARCHAR(128)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
                   )
        self.dtb.commit()
        cursor.close()

    def createCrimeTable(self):
        table_cmd = ("CREATE TABLE Crime ( X DOUBLE,\
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
                    occurrenceyear YEAR ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
                    )
        cursor = self.dtb.cursor()
        cursor.execute(table_cmd)
        self.dtb.commit()
        cursor.close()


    def insertUserData(self, userData):
        cursor = self.dtb.cursor()
        insert_cmd = f"INSERT INTO Users (fullname, username, password, email, phone, address) \
                        VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_cmd, (userData['fullname'], userData['username'], userData['password'], userData['email'], userData['phone'], userData['address']))
        self.dtb.commit()
        cursor.close()


    def insertCrimeDBData(self, emptyList, batch_size=1000):
        cursor = self.dtb.cursor(buffered=True)
        insert_cmd = """
        INSERT INTO Crime (
        ) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
        for i in range(0, len(emptyList), batch_size):
            batch = emptyList[i:i + batch_size]
            cursor.executemany(insert_cmd, batch)
            time.sleep(1)
            self.dtb.commit()
            print(f"[+] {i} Done")
        cursor.close()

    def dropTable(self, table):
        cursor = self.dtb.cursor()
        cursor.execute(f"DROP TABLE {table}")
        cursor.close()

    def getTableRecords(self, table):
        cursor = self.dtb.cursor()
        records_cmd = f"SELECT * FROM {table}"
        cursor.execute(records_cmd)
        print(cursor.column_names)
        print(cursor.fetchall())
        cursor.close()

    def validateUser(self, user):
        cursor = self.dtb.cursor()
        mask = f"SELECT  * FROM Users WHERE username = %s AND password = %s"
        cursor.execute(mask, user)
        return cursor.fetchone()


    def deleteUser(self, username):
        user = (username, )
        del_cmd = f"DELETE FROM Users WHERE username = %s"
        cursor = self.dtb.cursor()
        cursor.execute(del_cmd, user)
        self.dtb.commit()
        cursor.close()

    def close(self):
        self.dtb.close()

    def getUserData(self, username):
        usr = (username, )
        ud_cmd = "SELECT * FROM Users WHERE username = %s"
        cursor = self.dtb.cursor(dictionary=True)
        cursor.execute(ud_cmd, usr)
        query_results = cursor.fetchone()
        return query_results

    def updateUserData(self, new_data):
        try:
            cursor = self.dtb.cursor()
            update_query = """
            UPDATE Users
            SET fullname = %s, email = %s, phone = %s, address = %s
            WHERE username = %s
            """
            cursor.execute(update_query, (new_data['fullname'], new_data['email'], new_data['phone'], new_data['address'], new_data['username']))
            self.dtb.commit()

        except Exception as e:
            print(f"Error updating user profile: {e}")

        finally:
            cursor.close()

# with ThreadPoolExecutor(max_workers=2) as tpe:
#     tpe.map(fn=load_csv(csvInfo))

# dtb = DTB(dbConfig)
# dtb.updateUserData(adminConfig)
# print(dtb.getUserData('admin'))









