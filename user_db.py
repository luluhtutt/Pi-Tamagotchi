import sqlite3
import random
import cv2

connection = sqlite3.connect("user.db")

cursor = connection.cursor()

cursor.execute("CREATE TABLE imgfg(id string, img blob)")

connection.commit()
connection.close()
