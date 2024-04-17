import sqlite3
import random

connection = sqlite3.connect("tamagotchi.db")

cursor = connection.cursor()

cursor.execute("DROP TABLE IF EXISTS Tamagotchi")

tamagotchi_table = """ CREATE TABLE Tamagotchi (
    Name varchar(255),
    TID int NOT NULL PRIMARY KEY,
    Image varchar(255)
); """
cursor.execute(tamagotchi_table)

user_table = """ CREATE TABLE User (
    Name varchar(255),
    UID int NOT NULL PRIMARY KEY,
    Image varchar(255)
); """
cursor.execute(user_table)

relation_table = """ CREATE TABLE Relation (
    UID int NOT NULL PRIMARY KEY,
    TID int NOT NULL PRIMARY KEY,
    Age float,
    Health int,
    Hunger int,
    Happiness int
); """
cursor.execute(relation_table)

# create tamagotchis
images = ["fox.png", "sanaart.png", "zebra.png"]
names = ["Bob", "Pacmen", "Jaredz"]

for i in range(10):
    n = random.randint(0, len(images)-1)
    filename = images[n]
    name = names[n]
    add_tamagotchi =  """ INSERT INTO Tamagotchi VALUES ('""" + name + """', """ + str(i) + """, '""" + str(filename) + """')"""
    cursor.execute(add_tamagotchi)

connection.commit()

connection.close()
