import sqlite3
import random

connection = sqlite3.connect("tamagotchi.db")

cursor = connection.cursor()

cursor.execute("DROP TABLE IF EXISTS Tamagotchi")
cursor.execute("DROP TABLE IF EXISTS User")
cursor.execute("DROP TABLE IF EXISTS Relation")

tamagotchi_table = """ CREATE TABLE Tamagotchi (
    Name varchar(255),
    TID int NOT NULL PRIMARY KEY,
    Tim varchar(255)
); """
cursor.execute(tamagotchi_table)

user_table = """ CREATE TABLE User (
    Name varchar(255),
    UID int NOT NULL PRIMARY KEY,
    Uim varchar(255)
); """

cursor.execute(user_table)

relation_table = """ CREATE TABLE Relation (
    UID int NOT NULL,
    TID int NOT NULL,
    Age float,
    Health int,
    Hunger int,
    Happiness int,
    PRIMARY KEY (UID, TID)
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

add_user =  """ INSERT INTO User VALUES ('Lulu', 1, 'user_images/lulu1.jpg');"""
cursor.execute(add_user)
add_user =  """ INSERT INTO User VALUES ('Sana', 2, 'user_images/sana1.jpg');"""
cursor.execute(add_user)
add_relation = """ INSERT INTO Relation VALUES (1, 1, 0.5, 90, 80, 70);"""
cursor.execute(add_relation)


connection.commit()
connection.close()
