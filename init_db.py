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
images = ["tama1.png", "tama2.png", "tama3.png", "tama4.png", "tama5.png", "tama6.png", "tama7.png", "tama8.png", "tama9.png"]
names = ["Capyz", "Pacmen", "Jaredz", "Bob", "Kin gJuilan", "Jonathon", "Nola", "NYSEG", "Epty"]

for i in range(len(images)):
    filename = images[i]
    name = names[i]
    add_tamagotchi =  """ INSERT INTO Tamagotchi VALUES ('""" + name + """', """ + str(i+1) + """, '""" + str(filename) + """')"""
    cursor.execute(add_tamagotchi)

add_user =  """ INSERT INTO User VALUES ('Lulu', 1, 'user_images/lulu1.jpg');"""
cursor.execute(add_user)
add_user =  """ INSERT INTO User VALUES ('Sana', 2, 'user_images/sana1.jpg');"""
cursor.execute(add_user)
add_user =  """ INSERT INTO User VALUES ('Prakriti', 3, 'user_images/user3.jpg');"""
cursor.execute(add_user)
add_user =  """ INSERT INTO User VALUES ('Ananya', 4, 'user_images/user4.jpg');"""
cursor.execute(add_user)
add_user =  """ INSERT INTO User VALUES ('TA Michael', 5, 'user_images/user5.jpg');"""
cursor.execute(add_user)

add_relation = """INSERT INTO Relation VALUES (1, 5, 0, 80, 92, 60); """
cursor.execute(add_relation)
add_relation = """INSERT INTO Relation VALUES (1, 1, 0, 100, 10, 50); """
cursor.execute(add_relation)

connection.commit()
connection.close()
