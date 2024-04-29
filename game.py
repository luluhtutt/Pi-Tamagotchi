import pygame, pigame
from pygame.locals import * 
import os 
import time
import RPi.GPIO as GPIO
import subprocess
import sqlite3
from camera import * 
 
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
def choose_tama(TID):
    images_select = """ select Tim from Tamagotchi where TID = """ + str(TID) + """ limit 1;"""
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

def files():
    file_pos = [(20, 10), (20, 58), (20, 106), (20, 154), (20, 202), (180, 10), (180, 58), (180, 106), (180, 154), (180, 202)]
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
            text_surface = font_files.render('TID: ' + str(cur_tamas[t][1]), True, WHITE)
            rect = text_surface.get_rect(topleft=file_pos[t]) 
            lcd.blit(text_surface, rect)
        pygame.display.update()

times = {0: "12:00 AM", 15: "1:00 AM", 30: "2:00 AM", 45: "3:00 AM", 60: "4:00 AM", 75: "5:00 AM", 90: "6:00 AM", 105: "7:00 AM",
120: "8:00 AM", 135: "9:00 AM", 150: "10:00 AM", 165: "11:00 AM", 180: "12:00 PM", 195: "1:00 PM", 210: "2:00 PM", 225: "3:00 PM", 240: "4:00 PM", 
255: "5:00 PM", 270: "6:00 PM", 285: "7:00 PM", 300: "8:00 PM", 315: "9:00 PM", 330: "10:00 PM", 345: "11:00 PM"}

user_login_buttons = {'New Player': (160, 60), 'Returning Player': (160, 120), 'Quit': (160, 180)}
main_buttons = {'Menu': (20, 20), 'Quit':(20, 60)}
action_buttons = {'Info': (20, 20), 'Feed': (20,50), 'Sleep': (20, 80), 'Clean': (20, 110), 'Back': (20,140), 'Quit': (20,170)}

# state variables
time_counter = 0
playing = True
current_screen = 'login' # current_screen is either 'login', 'file', or 'main'
current_menu = 'main' # current_menu is either 'main', 'files', 'actions', or 'info'
selection_max = {'main': 2, 'files': 10, 'actions': 6}
selection = 0 # selection is the index of the menu item that is currently selected

def GPIO17_callback(channel):
    global selection
    selection = max(selection-1, 0)
    print("selection value: ", str(selection))

def GPIO22_callback(channel):
    global selection
    selection += 1
    print("selection value: ", str(selection))
    
def GPIO27_callback(channel):
    connection.commit()
    connection.close()
    pygame.quit() 
    import sys
    sys.exit(0)
    del(pitft)

GPIO.add_event_detect(17, GPIO.FALLING, callback=GPIO17_callback, bouncetime=300)
GPIO.add_event_detect(22, GPIO.FALLING, callback=GPIO22_callback, bouncetime=300)
GPIO.add_event_detect(27, GPIO.FALLING, callback=GPIO27_callback, bouncetime=300)

while(playing):
    # login screen
    if(current_screen == 'login'):
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
                    capture_image(fp)
                    current_screen = 'file'
                    
                elif(y > 90 and y < 150):
                    print("returning player")
                    UID = classify_image(cursor)
                    current_screen = 'file'
                    # print(UID)

                else:
                    print("quit pressed")
                    playing = False
                
    elif(current_screen == 'file'):
        files()
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

            pygame.draw.rect(lcd, (0,0,0), pygame.Rect(0, 0, 18, 200))
            pygame.display.update()

            location = main_buttons[list(main_buttons.keys())[min(selection, 1)]]
            text_surface = font_main_buttons.render('>', True, WHITE)
            rect = text_surface.get_rect(topleft=(location[0]-15, location[1]-3))
            lcd.blit(text_surface, rect)
            pygame.display.update()
        
        elif(current_menu == 'actions'):
            pygame.draw.rect(lcd, (0,0,0), pygame.Rect(0, 0, 120, 200))
            pygame.display.update()
            for k,v in action_buttons_buttons.items():
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
                selection = min(selection, 1)
                if(selection == 0):
                    current_menu = 'actions'
                else:
                    playing = False

        # check for taps
        pitft.update()
        for event in pygame.event.get():
            if(event.type is MOUSEBUTTONUP):
                x,y = pygame.mouse.get_pos()
                if(current_menu == 'main'):
                    # open actions menu
                    if(x < 50 and y < 80):
                        print("menu opened")
                        current_menu = 'actions'
                    # quit
                    elif(x > 50 and x < 90 and y < 80):
                        print("quit pressed")
                        playing = False
                # elif(current_menu == 'actions'):
                #     if(y < 80):
                #         if(x < )
        time_counter += 1
    time.sleep(1)

connection.commit()
connection.close()

pygame.quit() 
import sys
sys.exit(0)
del(pitft)
