import sqlite3 as sql

conn = sql.connect("iotuserinfo.db")
cur = conn.cursor()

# cur.execute("DROP TABLE IF EXISTS user")

# cur.execute("CREATE TABLE user(RFID_tag, username, email, temp_threshold, light_treshhold)")
# cur.execute('''
#     INSERT INTO user VALUES
#         (' 36 1f 56 91', 'Chris', 'nicolecanlapanb@gmail.com', 24, 200),
#         (' 76 47 50 91', 'Maxym', 'maxymgalenko@gmail.com', 23, 300),
#         (' c3 34 cc 19', 'Nicole', 'nicolecanlapanb@gmail.com', 23, 500)''')


# # Connect to a database
# conn = sql.connect('iotuserinfo.db')
# # Create a cursor
# cur = conn.cursor()
# # conn.execute('''DROP TABLE IF EXISTS user''') 
# # # Create user Table
# # conn.execute('''CREATE TABLE IF NOT EXISTS user 
# #                 (user_id integer, 
# #                 user_name text, 
# #                 temp_threshold integer,
# #                 hum_threshold integer,
# #                 light_intensity_threshold integer)
# #             ''') 

# cur.execute("INSERT INTO user (user_id, user_name, temp_threshold, hum_threshold, light_intensity_threshold) VALUES (NULL, 'Mubeenkh', 24, 60, 400)")
# cur.execute("INSERT INTO user (user_id, user_name, temp_threshold, hum_threshold, light_intensity_threshold) VALUES (NULL, 'RachelleBadua', 26, 70, 300)")
# cur.execute("INSERT INTO user (user_id, user_name, temp_threshold, hum_threshold, light_intensity_threshold) VALUES (NULL, NULL, NULL, NULL, NULL)")


# SELECT:
cur.execute("SELECT * FROM user")
conn.commit()
print(cur.fetchall())

# UPDATE:
# cur.execute("UPDATE user SET temp_threshold = 28, hum_threshold = 65 WHERE user_name = 'Mubeenkh'")
# cur.execute("SELECT * FROM user")
# conn.commit()
# print(cur.fetchall())

# DELETE:
# cur.execute("DELETE FROM user")
# cur.execute("SELECT * FROM user")
# conn.commit()
# print(cur.fetchall())




# Close DB object
cur.close()
conn.close()





