import pygame, pigame
from pygame.locals import * 
import os 
import time
import RPi.GPIO as GPIO
import subprocess
import sqlite3
# from camera import * 
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
font_action_buttons = pygame.font.Font(None, 18)
font_time = pygame.font.Font(None, 30)
font_files = pygame.font.Font(None, 20)

# displaying the tamagotchi
def display_tama_files(path, x, y, rescale):
    tama_im = pygame.image.load(path)
    tama_icon = pygame.transform.scale(tama_im, rescale)
    tama_rect_icon = tama_icon.get_rect()
    tama_rect_icon.x = x
    tama_rect_icon.y = y
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


# displaying status bars
def status_bars():
    cursor.execute(""" select Health from Relation where UID = """ + str(UID) + """ AND TID = """ + str(TID) + """;""")
    health = cursor.fetchone()[0]
    cursor.execute(""" select Happiness from Relation where UID = """ + str(UID) + """ AND TID = """ + str(TID) + """;""")
    happiness = cursor.fetchone()[0]
    cursor.execute(""" select Hunger from Relation where UID = """ + str(UID) + """ AND TID = """ + str(TID) + """;""")
    hunger = cursor.fetchone()[0]

    pygame.draw.rect(lcd, (255 ,255, 255), pygame.Rect(20, 210, 80, 15))
    pygame.draw.rect(lcd, (0, 255, 0), pygame.Rect(20, 210, 80*(hunger/100), 15))
    hunger_icon = pygame.image.load("images/hunger_bar.png")
    hunger_icon = pygame.transform.scale(hunger_icon, (19, 19))
    hunger_rect = hunger_icon.get_rect()
    hunger_rect.x = 8
    hunger_rect.y = 208
    lcd.blit(hunger_icon, hunger_rect)

    pygame.draw.rect(lcd, (255 ,255, 255), pygame.Rect(120, 210, 80, 15))
    pygame.draw.rect(lcd, (90, 100, 180), pygame.Rect(120, 210, 80*(health/100), 15))
    health_icon = pygame.image.load("images/health_bar.png")
    health_icon = pygame.transform.scale(health_icon, (19, 19))
    health_rect = health_icon.get_rect()
    health_rect.x = 108
    health_rect.y = 208
    lcd.blit(health_icon, health_rect)

    pygame.draw.rect(lcd, (255 ,255, 255), pygame.Rect(220, 210, 80, 15))
    pygame.draw.rect(lcd, (100, 255, 210), pygame.Rect(220, 210, 80*(happiness/100), 15))
    happy_icon = pygame.image.load("images/happy_bar.png")
    happy_icon = pygame.transform.scale(happy_icon, (19, 19))
    happy_rect = happy_icon.get_rect()
    happy_rect.x = 208
    happy_rect.y = 208
    lcd.blit(happy_icon, happy_rect)

    pygame.display.update()

def capture_image(fp):

    lcd.fill((0,0,0))
    pygame.display.update()

    camera = picamera.PiCamera()

    camera.start_preview()
    camera.resolution = (640, 480)

    font_cam = pygame.font.Font(None, 30)
    font_small = pygame.font.Font(None, 30)

    # Create a button to capture the frame
    capture_button = {"SMILE FOR THE CAMERA:)" : (160, 120)}
    for k,v in capture_button.items():
        text_surface = font_cam.render('%s'%k, True, WHITE)
        rect = text_surface.get_rect(center=v) 
        lcd.blit(text_surface, rect)

    for i in range(5, 0, -1): 
        time.sleep(1)
        pygame.draw.rect(lcd, (0,0,0), pygame.Rect(60, 40, 150, 50))
        pygame.display.update()
        k = str(i)
        text_surface_2 = font_small.render('%s'%k, True, WHITE)
        rect_2 = text_surface_2.get_rect(center=(120, 60)) 
        lcd.blit(text_surface_2, rect_2)
        pygame.display.update() 

    camera.capture(fp)
    camera.stop_preview()
    lcd.fill((0,0,0))
    pygame.display.update()

def classify_image(cursor):
    capture_image("user_images/test_im.jpg")
    new_face = fr.load_image_file("user_images/test_im.jpg")
    cursor.execute(""" select Uim from User;""")
    # old_face = fr.load_image_file(cursor.fetchall())
    old_faces = cursor.fetchall()
    old_encodings = [] 
    for face in old_faces:
        img = fr.load_image_file(face[0])
        # print(face[0])
        old_encodings.append(fr.face_encodings(img))
    # print(len(old_encodings))
    cursor.execute(""" select UID from User;""")
    names_list = cursor.fetchall()
    faces_names = [] 
    for names in names_list:
            faces_names.append(names[0])
    # print(len(faces_names))
    new_encoding = fr.face_encodings(new_face)[0]
    matches = fr.compare_faces(old_encodings, new_encoding)
    face_distances = fr.face_distance(old_encodings, new_encoding)
    face_sums = np.sum(face_distances, axis=1)
    best_match = np.argmin(face_sums)
    # print(matches)
    # print(best_match)
    name = faces_names[best_match]
    return name

times = {0: "12:00 AM", 15: "1:00 AM", 30: "2:00 AM", 45: "3:00 AM", 60: "4:00 AM", 75: "5:00 AM", 90: "6:00 AM", 105: "7:00 AM",
120: "8:00 AM", 135: "9:00 AM", 150: "10:00 AM", 165: "11:00 AM", 180: "12:00 PM", 195: "1:00 PM", 210: "2:00 PM", 225: "3:00 PM", 240: "4:00 PM", 
255: "5:00 PM", 270: "6:00 PM", 285: "7:00 PM", 300: "8:00 PM", 315: "9:00 PM", 330: "10:00 PM", 345: "11:00 PM"}

user_login_buttons = {'New Player': (160, 60), 'Returning Player': (160, 120), 'Quit': (160, 180)}
main_buttons = {'Menu': (20, 20), 'Quit':(20, 60)}
action_buttons = {'Info': (20, 20), 'Feed': (20,50), 'Sleep': (20, 80), 'Clean': (20, 110), 'Back': (20,140), 'Quit': (20,170)}
file_pos = [(20, 10), (20, 58), (20, 106), (20, 154), (20, 202), (180, 10), (180, 58), (180, 106), (180, 154), (180, 202)]

# state variables
time_counter = 0
playing = True
current_screen = 'file' # current_screen is either 'login', 'file', or 'main'
current_menu = 'files' # current_menu is either 'main', 'files', 'actions', or 'info'
selection_max = {'main': 1, 'files': 9, 'actions': 5}
selection = 0 # selection is the index of the menu item that is currently selected

def GPIO17_callback(channel):
    global selection
    selection = max(selection-1, 0)
    print("selection value: ", str(selection))

def GPIO22_callback(channel):
    global selection
    global selection_max
    selection = min(selection+1, selection_max[current_menu])
    # selection+=1
    print("selection value: ", str(selection))
    
def GPIO27_callback(channel):
    print("quit pressed")
    global playing
    playing = False

GPIO.add_event_detect(17, GPIO.FALLING, callback=GPIO17_callback, bouncetime=300)
GPIO.add_event_detect(22, GPIO.FALLING, callback=GPIO22_callback, bouncetime=300)
GPIO.add_event_detect(27, GPIO.FALLING, callback=GPIO27_callback, bouncetime=300)

while(playing):
    # login screen
    if(current_screen == 'login'):
        # current_screen = 'file'
        # current_menu = 'files'
        for k,v in user_login_buttons.items():
            text_surface = font_main_buttons.render('%s'%k, True, WHITE)
            rect = text_surface.get_rect(center=v) 
            lcd.blit(text_surface, rect)
        pygame.display.update()

        # check for taps
        pitft.update()
        for event in pygame.event.get():
            if(event.type is MOUSEBUTTONUP):
                x,y = pygame.mouse.get_pos()
                if(y < 90):
                    print("new player")
                    cursor.execute(""" SELECT COUNT(*) FROM User""")
                    UID = cursor.fetchone()[0] + 1
                    print("UID: ", UID)
                    fp = "user_images/user" + str(UID) + ".jpg"
                    user_name = "User" + str(UID)
                    cursor.execute("""INSERT INTO User VALUES ('""" + user_name + """' ,""" + str(UID) + """, '""" + fp + """');""")
                    connection.commit()
                    capture_image(fp)
                    current_screen = 'file'
                    current_menu = 'files'
                    
                elif(y > 90 and y < 150):
                    print("returning player")
                    UID = classify_image(cursor)
                    current_screen = 'file'
                    current_menu = 'files'
                    print(UID)

                else:
                    print("quit pressed")
                    playing = False
                
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
                # UID int NOT NULL,
                # TID int NOT NULL,
                # Age float,
                # Health int,
                # Hunger int,
                # Happiness int,
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

        # loop the counter
        if(time_counter >= 360):
            time_counter = -1
        
        if(current_menu == 'main'):
            # main buttons (menu, quit)

            for k,v in main_buttons.items():
                text_surface = font_main_buttons.render('%s'%k, True, WHITE)
                rect = text_surface.get_rect(topleft=v) 
                lcd.blit(text_surface, rect)
            pygame.display.update()
            
            cursor.execute("""SELECT * FROM Tamagotchi WHERE TID=""" + str(TID))
            tamas_info = cursor.fetchone()
            # print(tamas_info)
            tama_img_path = "images/" + str(tamas_info[2])

            display_tama_files(tama_img_path, 110 , 70, (100, 100))

            pygame.draw.rect(lcd, (0,0,0), pygame.Rect(0, 0, 18, 200))
            pygame.display.update()

            location = main_buttons[list(main_buttons.keys())[selection]]
            text_surface = font_main_buttons.render('>', True, WHITE)
            rect = text_surface.get_rect(topleft=(location[0]-15, location[1]-3))
            lcd.blit(text_surface, rect)
            pygame.display.update()
        
        elif(current_menu == 'actions'):
            pygame.draw.rect(lcd, (0,0,0), pygame.Rect(0, 0, 120, 200))
            pygame.display.update()
            for k,v in action_buttons.items():
                # pygame.draw.rect(lcd, (0,0,255), pygame.Rect(0, v[0]-20, 120, 40))
                text_surface = font_main_buttons.render('%s'%k, True, WHITE)
                rect = text_surface.get_rect(topleft=v) 
                lcd.blit(text_surface, rect)
            pygame.display.update()
            
        # status bars
        status_bars()

        # check if select is pressed
        if ( not GPIO.input(23)):
            if(current_menu == 'main'):
                if(selection == 0):
                    current_menu = 'actions'
                else:
                    playing = False

        # check for taps
        # pitft.update()
        # for event in pygame.event.get():
        #     if(event.type is MOUSEBUTTONUP):
        #         x,y = pygame.mouse.get_pos()
        #         if(current_menu == 'main'):
        #             # open actions menu
        #             if(x < 50 and y < 80):
        #                 print("menu opened")
        #                 current_menu = 'actions'
        #             # quit
        #             elif(x > 50 and x < 90 and y < 80):
        #                 print("quit pressed")
        #                 playing = False
                # elif(current_menu == 'actions'):
                #     if(y < 80):
                #         if(x < )
        time_counter += 0.1
    time.sleep(0.25)

print("loop finished")
connection.commit()
connection.close()
# pygame.quit() 
# import sys
# sys.exit(0)
# del(pitft)
