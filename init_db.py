import sqlite3
import random

connection = sqlite3.connect("tamagotchi.db")

cursor = connection.cursor()

cursor.execute("DROP TABLE IF EXISTS Tamagotchi")

tamagotchi_table = """ CREATE TABLE Tamagotchi (
    Name varchar(255),
    Id int NOT NULL PRIMARY KEY,
    Age float,
    Image varchar(255),
    Health int,
    Hunger int,
    Happiness int
); """
cursor.execute(tamagotchi_table)

images = ["fox.png", "sanaart.png", "zebra.png"]

for i in range(10):
    filename = images[random.randint(0, len(images)-1)]
    add_tamagotchi =  """ INSERT INTO Tamagotchi VALUES ('Test', """ + str(i) + """, 0.0, '""" + str(filename) + """', 100, 100, 100)"""
    cursor.execute(add_tamagotchi)

user_table = """ CREATE TABLE Tamagotchi (
    Name varchar(255),
    Id int NOT NULL PRIMARY KEY,
    Age float,
    Image varchar(255),
    Health int,
    Hunger int,
    Happiness int
); """

connection.commit()

connection.close()
