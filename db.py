import sqlite3

connection = sqlite3.connect("tamagotchi.db")

cursor = connection.cursor()

def set_health(uid, new_health):
    return """UPDATE Tamagotchi
    SET Health = """ + str(new_health) + """
    WHERE Id = """ + str(uid)

def set_hunger(uid, new_hunger):
    return """UPDATE Tamagotchi
    SET Hunger = """ + str(new_hunger) + """
    WHERE Id = """ + str(uid)

def set_happiness(uid, new_hunger):
    return """UPDATE Tamagotchi
    SET Hunger = """ + str(new_hunger) + """
    WHERE Id = """ + str(uid)

data = cursor.execute("""SELECT * FROM Tamagotchi""")
for row in data:
    print(row)

connection.close()
