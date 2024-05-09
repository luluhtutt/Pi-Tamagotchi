import pygame, pigame
from pygame.locals import * 
import os 
import time
import RPi.GPIO as GPIO
import subprocess
import sqlite3
from camera import * 
import random
import picamera
import cv2
import dlib as d
import face_recognition as fr
import numpy as np 
 
start = time.time()
# connect db
connection = sqlite3.connect("tamagotchi.db")
cursor = connection.cursor()

UID = 1
TID = 1
# pygame initialization
WHITE = (255,255,255)

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP) # up
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP) # down
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP) # select

os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDRV', 'dummy')
os.putenv('SDL_MOUSEDEV', '/dev/null')
os.putenv('DISPLAY', '')

pygame.init() 
pygame.mouse.set_visible(False)

pitft = pigame.PiTft()
size = width, height = 320,240
lcd = pygame.display.set_mode((width, height))
lcd.fill((0,0,0))
pygame.display.update()

# camera = PiCamera() 
# camera.start_preview()

# font settings
font_main_buttons = pygame.font.Font(None, 25)
font_action_buttons = pygame.font.Font(None, 20)
font_time = pygame.font.Font(None, 30)
font_files = pygame.font.Font(None, 20)

# displaying the tamagotchi
def display_tama_files(path, x, y, rescale):
    tama_im = pygame.image.load(path)
    tama_icon = pygame.transform.scale(tama_im, rescale)
    tama_rect_icon = tama_icon.get_rect()
    # print("x: ", x)
    # print("type x: ", type(x))
    tama_rect_icon.x = int(x)
    tama_rect_icon.y = int(y)
    lcd.blit(tama_icon, tama_rect_icon)

def get_user_data(UID, TID):
    images_select = """ select * from Relation where TID = """ + str(TID) + """ AND UID = """ + str(UID) +  """ limit 1;"""
    cursor.execute(images_select)
    image_path = "images/" + cursor.fetchone()[0]
    tama_im = pygame.image.load(image_path)
    tama_im = pygame.transform.scale(tama_im, (100, 100))
    tama_icon = pygame.transform.scale(tama_im, (35, 35))
    tama_rect = tama_im.get_rect()
    tama_rect.x = 110
    tama_rect.y = 70

def get_status(): 
    global UID
    global TID 
    global cursor
    cursor.execute(""" select Health from Relation where UID = """ + str(UID) + """ AND TID = """ + str(TID) + """;""")
    health = cursor.fetchone()[0]
    cursor.execute(""" select Happiness from Relation where UID = """ + str(UID) + """ AND TID = """ + str(TID) + """;""")
    happiness = cursor.fetchone()[0]
    cursor.execute(""" select Hunger from Relation where UID = """ + str(UID) + """ AND TID = """ + str(TID) + """;""")
    hunger = cursor.fetchone()[0]
    cursor.execute(""" select Age from Relation where UID = """ + str(UID) + """ AND TID = """ + str(TID) + """;""")
    age = cursor.fetchone()[0]
    cursor.execute(""" select Name from Tamagotchi where TID = """ + str(TID) + """;""")
    name = cursor.fetchone()[0]

    return [name, age, health, hunger, happiness]

def set_status(age, health, hunger, happiness):
    global UID
    global TID
    global connection
    global cursor
    cursor.execute(""" UPDATE Relation SET Health = """ + str(health) + """ where UID = """ + str(UID) + """ AND TID = """ + str(TID) + """;""")
    cursor.execute(""" UPDATE Relation SET Happiness = """ + str(happiness) + """ where UID = """ + str(UID) + """ AND TID = """ + str(TID) + """;""")
    cursor.execute(""" UPDATE Relation SET Hunger = """ + str(hunger) + """ where UID = """ + str(UID) + """ AND TID = """ + str(TID) + """;""")
    cursor.execute(""" UPDATE Relation SET Age = """ + str(age) + """ where UID = """ + str(UID) + """ AND TID = """ + str(TID) + """;""")
    connection.commit()
    return

# displaying status bars
def status_bars():
    
    [_, _, health, hunger, happiness] = get_status()

    pygame.draw.rect(lcd, (255 ,255, 255), pygame.Rect(20, 210, 80, 15))
    pygame.draw.rect(lcd, (90, 100, 180), pygame.Rect(20, 210, min(80, 80*(health/100)), 15))
    health_icon = pygame.image.load("images/health_bar.png")
    health_icon = pygame.transform.scale(health_icon, (19, 19))
    health_rect = health_icon.get_rect()
    health_rect.x = 8
    health_rect.y = 208
    lcd.blit(health_icon, health_rect)

    pygame.draw.rect(lcd, (255 ,255, 255), pygame.Rect(120, 210, 80, 15))
    pygame.draw.rect(lcd, (0, 255, 0), pygame.Rect(120, 210, min(80, 80*(hunger/100)), 15))
    hunger_icon = pygame.image.load("images/hunger_bar.png")
    hunger_icon = pygame.transform.scale(hunger_icon, (19, 19))
    hunger_rect = hunger_icon.get_rect()
    hunger_rect.x = 108
    hunger_rect.y = 208
    lcd.blit(hunger_icon, hunger_rect)

    pygame.draw.rect(lcd, (255 ,255, 255), pygame.Rect(220, 210, 80, 15))
    pygame.draw.rect(lcd, (100, 255, 210), pygame.Rect(220, 210, min(80, 80*(happiness/100)), 15))
    happy_icon = pygame.image.load("images/happy_bar.png")
    happy_icon = pygame.transform.scale(happy_icon, (19, 19))
    happy_rect = happy_icon.get_rect()
    happy_rect.x = 208
    happy_rect.y = 208
    lcd.blit(happy_icon, happy_rect)

    pygame.display.update()

def feed(cursor, lcd, img_path):
    [_, age, health, hunger, happiness] = get_status()
    global playing
    global tama_x
    global tama_y
    start_time = time.time() 
    end_time = start_time + 30 
    food_x = random.randint(10, 290)
    food_y = 0

    while playing and time.time() < end_time:
        # displaying the tama
        pygame.draw.rect(lcd, (0 ,0, 0), pygame.Rect(tama_x-20, tama_y, 100, 60))
        pygame.display.update()
        display_tama_files(img_path, tama_x, tama_y, (60, 60))
        pygame.display.update()

        # displaying the food
        pygame.draw.rect(lcd, (0 ,0, 0), pygame.Rect(food_x, food_y-3, 30, 36))
        pygame.display.update()
        display_tama_files("images/hunger_bar.png", food_x, food_y, (30, 30))
        pygame.display.update()
        food_y += 3

        if(food_y > 150):
            pygame.draw.rect(lcd, (0 ,0, 0), pygame.Rect(food_x, food_y-3, 30, 36))
            food_y = 0
            food_x = random.randint(10, 290)
            
        if(abs(food_x - tama_x) < 35 and abs(food_y - tama_y) < 35):
            print("ate!")
            pygame.draw.rect(lcd, (0 ,0, 0), pygame.Rect(food_x, food_y-3, 30, 36))
            food_y = 0
            food_x = random.randint(10, 310)
            [_, age, health, hunger, happiness] = get_status()
            set_status(age, health, int(hunger)+10, happiness)
            if (int(hunger)+10) >= 100: 
                break
            status_bars()

        time.sleep(0.1)
    pygame.draw.rect(lcd, (0 ,0, 0), pygame.Rect(food_x, food_y-3, 30, 36))
    pygame.draw.rect(lcd, (0 ,0, 0), pygame.Rect(tama_x-20, tama_y, 100, 60))
    pygame.display.update()

    return

def clean(cursor, lcd):
    print("clean called")
    [_, age, health, hunger, happiness] = get_status()
    # set_status(age, health, 0, happiness)
    global poops
    print("poops: ")
    indices = []
    for p in poops:
            display_tama_files(p[0], p[1], p[2], (20, 20))
            pygame.display.update()
    while (np.shape(poops)[0]) != 0: 
        # print("poop size: ", np.shape(poops)[0])
        pitft.update()
        for event in pygame.event.get():
            [_, age, health, hunger, happiness] = get_status()
            if(event.type is MOUSEBUTTONDOWN): 
                print("tap detected")
                x,y = pygame.mouse.get_pos()
                distance_thresh = 70
                print("x: ", x)
                print("y: ", y)
                x_diff = np.abs(poops[:, 1].astype(int) - x)
                y_diff = np.abs(poops[:, 2].astype(int) - y)
                # Find the indices where the condition is satisfied
                within_threshold = np.logical_and(x_diff <= distance_thresh, y_diff <= distance_thresh)
                indices = np.where(within_threshold)[0]
                # print("poops to check x and y: ", poops[:, 1:])
                # indices = np.argwhere(np.any(np.any(np.abs(poops[:,1].astype(int) - x) < 70) & np.any(np.abs(poops[:,2].astype(int) - y) < 70)))
                print("indices if ", indices)
                print("poops else ", poops)
                if(indices.size > 0):
                    print("indices shape: ", np.shape(indices))
                    print("indices else ", indices)
                    print("poops else ", poops)
                    for i in indices[::-1]: 
                        print("index ", i)
                        p = poops[i]
                        print("p: ", p)
                        pygame.draw.rect(lcd, (0,0,0), pygame.Rect(int(p[1]), int(p[2]), 20, 20))
                        pygame.display.update()
                        poops = np.delete(poops, i, axis = 0)
                        print("poops after deleting ", poops)
                    set_status(age, health + np.shape(indices)[0]*5, hunger, happiness)
                    
    return

times = {0: "12:00 AM", 15: "1:00 AM", 30: "2:00 AM", 45: "3:00 AM", 60: "4:00 AM", 75: "5:00 AM", 90: "6:00 AM", 105: "7:00 AM",
120: "8:00 AM", 135: "9:00 AM", 150: "10:00 AM", 165: "11:00 AM", 180: "12:00 PM", 195: "1:00 PM", 210: "2:00 PM", 225: "3:00 PM", 240: "4:00 PM", 
255: "5:00 PM", 270: "6:00 PM", 285: "7:00 PM", 300: "8:00 PM", 315: "9:00 PM", 330: "10:00 PM", 345: "11:00 PM"}

user_login_buttons = {'New Player': (100, 60), 'Returning Player': (100, 120), 'Quit': (100, 180)}
main_buttons = {'Menu': (20, 20), 'Quit':(20, 60)}
action_buttons = {'Info': (20, 20), 'Feed': (20,50), 'Sleep': (20, 80), 'Clean': (20, 110), 'Back': (20,140), 'Quit': (20,170)}
file_pos = [(20, 10), (20, 58), (20, 106), (20, 154), (20, 202), (180, 10), (180, 58), (180, 106), (180, 154), (180, 202)]
death_buttons = {'Tamagotchis': (20,80), 'Quit': (20, 160)}
info_info = {'TID': (20, 18), 'Name': (20, 40), 'Age': (20, 62), 'Health': (20, 84), 'Hunger': (20, 106), 'Happiness': (20, 128), 'Back': (20, 150), 'Quit': (20, 172)} 

# state variables
time_counter = 0
playing = True
current_screen = 'login' # current_screen is either 'login', 'file', or 'main' or 'death'
current_menu = 'login' # current_menu is either 'login', 'main', 'files', 'actions', 'info', or 'death'
selection_max = {'login': 2, 'main': 1, 'files': 9, 'actions': 5, 'info': 7, 'death': 1}
selection = 0 # selection is the index of the menu item that is currently selected
action = False
tama_x = 110
tama_y = 120
poops = np.array([])

def GPIO17_callback(channel):
    global action
    print("action; ", action)
    if(action):
        print("left!")
        global tama_x
        tama_x = max(0, tama_x-20)
    else:
        global selection
        selection = max(selection-1, 0)
        print("selection value: ", str(selection))

def GPIO22_callback(channel):
    global action
    print("action; ", action)
    if(action):
        print("right!")
        global tama_x
        tama_x = min(320, tama_x+20)
    else:
        global selection
        global selection_max
        selection = min(selection+1, selection_max[current_menu])
        print("selection value: ", str(selection))
    
def GPIO27_callback(channel):
    print("quit pressed")
    global playing
    playing = False

GPIO.add_event_detect(17, GPIO.FALLING, callback=GPIO17_callback, bouncetime=300)
GPIO.add_event_detect(22, GPIO.FALLING, callback=GPIO22_callback, bouncetime=300)
GPIO.add_event_detect(27, GPIO.FALLING, callback=GPIO27_callback, bouncetime=300)

# TODO
# emotion detection for happiness
# when health = 0, dies
# when tamagotchi dies, remove from the database
# hardware
# portable battery/charging port
# crontab

while(playing):
    # login screen
    if(current_screen == 'login'):
        for k,v in user_login_buttons.items():
            text_surface = font_main_buttons.render('%s'%k, True, WHITE)
            rect = text_surface.get_rect(topleft=v) 
            lcd.blit(text_surface, rect)
        pygame.display.update()

        pygame.draw.rect(lcd, (0,0,0), pygame.Rect(80, 0, 18, 200))
        pygame.display.update()

        # login menu selection arrow
        location = user_login_buttons[list(user_login_buttons.keys())[selection]]
        text_surface = font_main_buttons.render('>', True, WHITE)
        rect = text_surface.get_rect(topleft=(location[0]-15, location[1]-3))
        lcd.blit(text_surface, rect)
        pygame.display.update()

        if ( not GPIO.input(23)):
            if(selection == 0): # new player
                print("new player")
                cursor.execute(""" SELECT COUNT(*) FROM User""")
                UID = cursor.fetchone()[0] + 1
                print("UID: ", UID)
                fp = "user_images/user" + str(UID) + ".jpg"
                user_name = "User" + str(UID)
                cursor.execute("""INSERT INTO User VALUES ('""" + user_name + """' ,""" + str(UID) + """, '""" + fp + """');""")
                connection.commit()
                capture_image(fp, lcd)
                selection = 0
                current_screen = 'file'
                current_menu = 'files'
            elif(selection == 1): # returning player
                selection = 0
                print("returning player")
                UID = classify_image(cursor, lcd)
                # if UID: 
                current_screen = 'file'
                current_menu = 'files'
                print(UID)
            else:
                print("quit pressed")
                playing = False
    
    # tama selection screen
    elif(current_screen == 'file'):
        lcd.fill((0, 0, 0))
        cursor.execute("""SELECT DISTINCT TID FROM Tamagotchi""")
        all_tama = cursor.fetchall() 
        # print(all_tama)
        all_tama_tids = [] 
        for t in all_tama: 
            # print(t)
            # print(type(t[0]))
            all_tama_tids.append(str(t[0]))
        # print(all_tama_tids)
        list_tamas = []
        cursor.execute("""SELECT * FROM Relation WHERE UID=""" + str(UID))
        cur_tamas = cursor.fetchall()
        cur_tamas.extend([None] * (10 - len(cur_tamas)))
        # print("cur tamas: ", cur_tamas)
        for t in range(len(cur_tamas)):
            if(cur_tamas[t] is None):
                text_surface = font_files.render('EMPTY', True, WHITE)
                rect = text_surface.get_rect(topleft=file_pos[t]) 
                lcd.blit(text_surface, rect)
            else:
                tama_tid = str(cur_tamas[t][1])
                # print(type(tama_tid))
                all_tama_tids.remove(tama_tid)
                cursor.execute("""SELECT * FROM Tamagotchi WHERE TID=""" + str(tama_tid))
                tamas_info = cursor.fetchone()
                # print(tamas_info)
                tama_name = str(tamas_info[0])
                tama_img_path = "images/" + str(tamas_info[2])
                # print(tama_img_path)
                text_surface = font_files.render(str(cur_tamas[t][1]) + ". " + str(tama_name), True, WHITE)
                display_tama_files(tama_img_path, file_pos[t][0] + 100, file_pos[t][1], (35, 35))
                rect = text_surface.get_rect(topleft=file_pos[t]) 
                lcd.blit(text_surface, rect)
            pygame.display.update()

        pygame.draw.rect(lcd, (0,0,0), pygame.Rect(0, 0, 18, 240))
        pygame.display.update()

        pygame.draw.rect(lcd, (0,0,0), pygame.Rect(163, 0, 18, 240))
        pygame.display.update()

        location = file_pos[selection]
        text_surface = font_main_buttons.render('>', True, WHITE)
        rect = text_surface.get_rect(topleft=(location[0]-15, location[1]-3))
        lcd.blit(text_surface, rect)
        pygame.display.update()

        # check if select is pressed
        if ( not GPIO.input(23)):
            if(cur_tamas[selection] is None):
                rand_in = random.randint(0, (len(all_tama_tids) - 1))
                selected_tama = all_tama_tids[rand_in]
                add_relation = """INSERT INTO Relation VALUES (""" + str(UID) + """,""" + str(selected_tama) + """, 0, 100, 100, 100);"""
                cursor.execute(add_relation)
                connection.commit()
            else: 
                # print("tama selected")
                TID = cur_tamas[selection][1]
                current_menu = 'main'
                current_screen = "main"
                lcd.fill((0,0,0))
                pygame.display.update()
            selection = 0


    # main screen
    elif(current_screen == 'main'):
        # printing time
        if(time_counter % 15 == 0):

            pygame.draw.rect(lcd, (0,0,0), pygame.Rect(200, 10, 120, 30))
            pygame.display.update()

            k = times[time_counter]
            time_surface = font_time.render('%s'%k, True, WHITE)
            time_rect = time_surface.get_rect(center=(260, 20)) 
            lcd.blit(time_surface, time_rect)
            pygame.display.update()

        if(time_counter % 15 == 7):
            # add a poop every hour
            poop_index = random.randint(1,2)
            poop_x = random.randint(10, 290)
            poop_y = random.randint(170, 190)
            if(poops.shape[0] == 0):
                poops = np.array([["images/poop" + str(poop_index) + ".png", int(poop_x), int(poop_y)]])
            else:
                poops = np.append(poops, [["images/poop" + str(poop_index) + ".png", int(poop_x), int(poop_y)]], axis=0)
            # print("poops: ", poops)
            [name, age, health, hunger, happiness] = get_status()
            new_health = max(0, health - np.shape(poops)[0] * 5)
            set_status(age, new_health, hunger, happiness)

        # decrement hunger
        if(time_counter % 15 == 3 or time_counter % 15 == 12):
            [name, age, health, hunger, happiness] = get_status()
            hunger_dec = random.randint(2, 9)
            hunger = max(0, hunger - hunger_dec)
            set_status(age, health, hunger, happiness)

        # when hunger = 0, health goes down
        # when hunger < 50, happiness goes down
        if(time_counter % 5 == 0):
            [name, age, health, hunger, happiness] = get_status()
            if(hunger < 50):
                if(hunger == 0):
                    health /= 2
                else:
                    happiness *= 0.9
                set_status(age, health, hunger, happiness)

        # if happiness is low, decrease health
        [name, age, health, hunger, happiness] = get_status()
        if(happiness < 5):
            set_status(age, health*0.9, hunger, happiness)

        # loop the time counter
        if(time_counter >= 359):
            # increment age
            [name, age, health, hunger, happiness] = get_status()
            set_status(age+1, health, hunger, happiness)
            time_counter = -1
        
        # black rect to remove actions
        pygame.draw.rect(lcd, (0,0,0), pygame.Rect(110, 50, 210, 150))
        pygame.display.update()

        # get tamagotchi information
        cursor.execute("""SELECT * FROM Tamagotchi WHERE TID=""" + str(TID))
        tamas_info = cursor.fetchone()
        # print(tamas_info)
        tama_img_path = "images/" + str(tamas_info[2])

        display_tama_files(tama_img_path, 110 , 70, (100, 100))

        # black for menu arrows
        pygame.draw.rect(lcd, (0,0,0), pygame.Rect(0, 0, 18, 200))
        pygame.display.update()
        
        if(current_menu == 'main'):
            pygame.draw.rect(lcd, (0,0,0), pygame.Rect(20, 0, 90, 200))
            pygame.display.update()
            # main buttons (menu, quit)
            for k,v in main_buttons.items():
                text_surface = font_main_buttons.render('%s'%k, True, WHITE)
                rect = text_surface.get_rect(topleft=v) 
                lcd.blit(text_surface, rect)
            pygame.display.update()

            # main menu selection arrow
            location = main_buttons[list(main_buttons.keys())[selection]]
            text_surface = font_main_buttons.render('>', True, WHITE)
            rect = text_surface.get_rect(topleft=(location[0]-15, location[1]-3))
            lcd.blit(text_surface, rect)
            pygame.display.update()

            # check if select is pressed
            if ( not GPIO.input(23)):
                if(selection == 0):
                    current_menu = 'actions'
                else:
                    playing = False
        
        elif (current_menu == 'info'): 
            pygame.draw.rect(lcd, (0,0,0), pygame.Rect(20, 0, 190, 200))
            # display_tama_files(tama_img_path, 110 , 70, (100, 100))
            pygame.display.update()

            information = get_status()  
            information = [TID, ] + information
            i = 0
            # print tama info 
            for k,v in info_info.items():
                if i < len(information):
                    k = k + ": " + str(information[i])
                    i += 1
                text_surface = font_action_buttons.render('%s'%k, True, WHITE)
                rect = text_surface.get_rect(topleft=v) 
                lcd.blit(text_surface, rect)
            pygame.display.update()

            pygame.draw.rect(lcd, (0,0,0), pygame.Rect(0, 0, 18, 200))
            pygame.display.update()

            display_tama_files(tama_img_path, 160 , 70, (100, 100))

            # info menu back and quit 
            location = info_info[list(info_info.keys())[selection]]
            text_surface = font_main_buttons.render('>', True, WHITE)
            rect = text_surface.get_rect(topleft=(location[0]-15, location[1]-3))
            lcd.blit(text_surface, rect)
            pygame.display.update()
            
            # check info menu back/quit
            if ( not GPIO.input(23)):
                if(selection == 6):
                    selection = 0
                    current_menu = 'actions'
                    pygame.draw.rect(lcd, (0,0,0), pygame.Rect(0, 0, 210, 200))
                elif(selection == 7):
                    playing = False
            
        elif(current_menu == 'actions'):
            pygame.draw.rect(lcd, (0,0,0), pygame.Rect(20, 0, 90, 200))
            pygame.display.update()
            # action menu items
            for k,v in action_buttons.items():
                # pygame.draw.rect(lcd, (0,0,255), pygame.Rect(0, v[0]-20, 120, 40))
                text_surface = font_main_buttons.render('%s'%k, True, WHITE)
                rect = text_surface.get_rect(topleft=v) 
                lcd.blit(text_surface, rect)
            pygame.display.update()

            pygame.draw.rect(lcd, (0,0,0), pygame.Rect(0, 0, 18, 200))
            pygame.display.update()

            # action menu selection arrow
            location = action_buttons[list(action_buttons.keys())[selection]]
            text_surface = font_main_buttons.render('>', True, WHITE)
            rect = text_surface.get_rect(topleft=(location[0]-15, location[1]-3))
            lcd.blit(text_surface, rect)
            pygame.display.update()

            # check if select is pressed
            if ( not GPIO.input(23)):
                if(selection == 0):
                    selection = 6
                    current_menu = 'info'
                elif(selection == 1): # feed
                    action = True
                    pygame.draw.rect(lcd, (0,0,0), pygame.Rect(0, 0, 320, 200))
                    pygame.display.update()
                    feed(cursor, lcd, tama_img_path)
                    selection = 0
                    current_menu = 'actions'
                    action = False
                elif(selection == 2): # sleep
                    selection = 0
                    sleep(cursor, lcd)
                elif(selection == 3): # clean
                    pygame.draw.rect(lcd, (0,0,0), pygame.Rect(0, 0, 110, 200))
                    pygame.display.update()
                    clean(cursor, lcd)
                    selection = 0
                elif(selection == 4): # 
                    selection = 0
                    current_menu = 'main'
                else:
                    print("quit pressed")
                    playing = False
        
        # print the poops
        for p in poops:
            display_tama_files(p[0], p[1], p[2], (20, 20))
            pygame.display.update()

        # status bars
        status_bars()

        # check if dead
        [name, age, health, hunger, happiness] = get_status()
        if(health == 0):
            current_screen = 'death'
            current_menu = 'death'

        time_counter += 0.25

    # death screen    
    elif(current_screen == 'death'):
        lcd.fill((0,0,0))
        display_tama_files("images/tombstone.png", 180, 70, (120, 160))

        for k,v in death_buttons.items():
            # pygame.draw.rect(lcd, (0,0,255), pygame.Rect(0, v[0]-20, 120, 40))
            text_surface = font_main_buttons.render('%s'%k, True, WHITE)
            rect = text_surface.get_rect(topleft=v) 
            lcd.blit(text_surface, rect)
        pygame.display.update()

        pygame.draw.rect(lcd, (0,0,0), pygame.Rect(0, 0, 18, 200))
        pygame.display.update()

        # death menu selection arrow
        location = death_buttons[list(death_buttons.keys())[selection]]
        text_surface = font_main_buttons.render('>', True, WHITE)
        rect = text_surface.get_rect(topleft=(location[0]-15, location[1]-3))
        lcd.blit(text_surface, rect)
        pygame.display.update()

        cursor.execute(""" DELETE from Relation where TID = """ + str(TID) + """ AND UID = """ + str(UID) +  """;""")
        connection.commit()
        pygame.display.update()

        if ( not GPIO.input(23)):
            if(selection == 0): # files
                lcd.fill((0,0,0))
                selection = 0
                current_screen = 'file'
                current_menu = 'files'
            else:
                print("quit pressed")
                playing = False

    
    time.sleep(0.25)

print("loop finished")
pygame.quit()
GPIO.cleanup()
connection.commit()
connection.close()
# pygame.quit() 
# import sys
# sys.exit(0)
# del(pitft)

