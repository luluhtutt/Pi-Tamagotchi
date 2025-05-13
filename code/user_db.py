import sqlite3
import random
import cv2

connection = sqlite3.connect("user.db")

cursor = connection.cursor()

user_table = """ CREATE TABLE User (
    Name varchar(255),
    UID int NOT NULL PRIMARY KEY,
    Uim varchar(255)
); """

cursor.execute(user_table)

add_user =  """ INSERT INTO User VALUES ('Lulu', 1, 'user_images/lulu1.jpg');"""
cursor.execute(add_user)
add_user =  """ INSERT INTO User VALUES ('Sana', 2, 'user_images/sana1.jpg');"""
cursor.execute(add_user)

connection.commit()
connection.close()
