import pygame, pigame
from pygame.locals import * 
import os 
import time
import RPi.GPIO as GPIO
import subprocess
import sqlite3
 
start = time.time()
# connect db
connection = sqlite3.connect("../tamagotchi.db")
cursor = connection.cursor()

UID = 1
TID = 1
# pygame initialization
WHITE = (255,255,255)

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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

font_big = pygame.font.Font(None, 40)
font_main_buttons = pygame.font.Font(None, 25)
font_time = pygame.font.Font(None, 30)

# displaying the tamagotchi
images_select = """ select Tim from Tamagotchi where TID = """ + str(TID) + """ limit 1;"""
cursor.execute(images_select)

image_path = "images/" + cursor.fetchone()[0]
tama_im = pygame.image.load(image_path)
tama_im = pygame.transform.scale(tama_im, (100, 100))
tama_rect = tama_im.get_rect()
tama_rect.x = 110
tama_rect.y = 70

lcd.blit(tama_im, tama_rect)
pygame.display.update()

# displaying status bars
get_health = """ select Health from Relation where UID = """ + str(UID) + """ AND TID = """ + str(TID) + """;"""
get_happy = """ select Happiness from Relation where UID = """ + str(UID) + """ AND TID = """ + str(TID) + """;"""
get_hunger = """ select Hunger from Relation where UID = """ + str(UID) + """ AND TID = """ + str(TID) + """;"""
cursor.execute(get_health)
health = cursor.fetchone()[0]
# print("health: ", cursor.fetchone()[0])
cursor.execute(get_happy)
happiness = cursor.fetchone()[0]
# print("happy: ", cursor.fetchone()[0])
cursor.execute(get_hunger)
hunger = cursor.fetchone()[0]

pygame.draw.rect(lcd, (255 ,255, 255), pygame.Rect(20, 210, 80, 15))
pygame.draw.rect(lcd, (0, 255, 0), pygame.Rect(20, 210, 80*(hunger/100), 15))

pygame.draw.rect(lcd, (255 ,255, 255), pygame.Rect(120, 210, 80, 15))
pygame.draw.rect(lcd, (90, 100, 180), pygame.Rect(120, 210, 80*(health/100), 15))

pygame.draw.rect(lcd, (255 ,255, 255), pygame.Rect(220, 210, 80, 15))
pygame.draw.rect(lcd, (100, 255, 210), pygame.Rect(220, 210, 80*(happiness/100), 15))

pygame.display.update()

times = {0: "12:00 AM", 15: "1:00 AM", 30: "2:00 AM", 45: "3:00 AM", 60: "4:00 AM", 75: "5:00 AM", 90: "6:00 AM", 105: "7:00 AM",
120: "8:00 AM", 135: "9:00 AM", 150: "10:00 AM", 165: "11:00 AM", 180: "12:00 PM", 195: "1:00 PM", 210: "2:00 PM", 225: "3:00 PM", 240: "4:00 PM", 
255: "5:00 PM", 270: "6:00 PM", 285: "7:00 PM", 300: "8:00 PM", 315: "9:00 PM", 330: "10:00 PM", 345: "11:00 PM"}

main_buttons = {'Menu': (40, 20), 'Quit':(40, 50)}

# menu_buttons = {'Info': (0, 0), 'Quit': (0,0): 'Feed': (0,0), ''}

time_counter = 0

playing = True
while(playing):
    # printing time
    if(time_counter % 15 == 0):
        pygame.draw.rect(lcd, (0,0,0), pygame.Rect(200, 10, 120, 30))
        pygame.display.update()

        k = times[time_counter]
        time_surface = font_time.render('%s'%k, True, WHITE)
        time_rect = time_surface.get_rect(center=(260, 20)) 
        lcd.blit(time_surface, time_rect)
        pygame.display.update()

    if(time_counter >= 360):
        time_counter = -1
    
    for k,v in main_buttons.items(): 
            text_surface = font_main_buttons.render('%s'%k, True, WHITE)
            rect = text_surface.get_rect(center=v) 
            lcd.blit(text_surface, rect)

    pygame.display.update()
    
    time.sleep(1)
    time_counter += 1

# print("hungry: ", cursor.fetchone()[0])

# touch_buttons = {'Start': (80, 180), 'Quit':(240, 180)}

# play_buttons = {'Pause': (40, 200), 'Fast': (120, 200), 'Slow': (200, 200), 'Back': (280, 200)}

# screen_taps = [] 

# pygame.display.update() 

# time_end = time.time() + 60

# sleep_time = 0.01

# can_start = False
# code_quit = True
# pause_game = False

# while (code_quit and time.time() < time_end): 
#     if ( not GPIO.input(17)):
#         break

#     pitft.update()

#     if(can_start):
#         if(not pause_game):
#             christmas_ballrect = christmas_ballrect.move(speed)
#             bballrect = bballrect.move(b_speed)
#             if bballrect.colliderect(christmas_ballrect):
#                 speed[0] = -speed[1]
#                 speed[1] = -speed[0]
#                 b_speed[0] = -b_speed[1] 
#                 b_speed[1] = -b_speed[0]
#             if christmas_ballrect.left < 0 or christmas_ballrect.right > width:
#                 speed[0] = -speed[0]
#             if christmas_ballrect.top < 0 or christmas_ballrect.bottom > height:
#                 speed[1] = -speed[1]
#             if bballrect.left < 0 or bballrect.right > width:
#                 b_speed[0] = -b_speed[0]
#             if bballrect.top < 0 or bballrect.bottom > height:
#                 b_speed[1] = -b_speed[1]

#         lcd.fill(black)
#         lcd.blit(christmas_ball, christmas_ballrect)
#         lcd.blit(bball, bballrect)

#         for k,v in play_buttons.items(): 
#             text_surface = font_small.render('%s'%k, True, WHITE)
#             rect = text_surface.get_rect(center=v) 
#             lcd.blit(text_surface, rect)

#     else:
#         for k,v in touch_buttons.items(): 
#             text_surface = font_big.render('%s'%k, True, WHITE)
#             rect = text_surface.get_rect(center=v) 
#             lcd.blit(text_surface, rect) 

#     pygame.display.update()
    
#     for event in pygame.event.get(): 
#         if(event.type is MOUSEBUTTONDOWN): 
#             x,y = pygame.mouse.get_pos()  
#             if y < 120: 
#                 screen_taps.append((x,y))
#                 pygame.draw.rect(lcd, (0,0,0), pygame.Rect(60, 40, 150, 50))
#                 pygame.display.update()
#                 k = 'touch at ' + str(screen_taps[-1])
#                 text_surface_2 = font_small.render('%s'%k, True, WHITE)
#                 rect_2 = text_surface_2.get_rect(center=(120, 60)) 
#                 lcd.blit(text_surface_2, rect_2)
#                 pygame.display.update() 
#                 print("button down")
#                 print(x, y)
#         elif (event.type is MOUSEBUTTONUP): 
#             x,y = pygame.mouse.get_pos()
#             if(not can_start):
#                 if y >= 120 and x < 100: 
#                     can_start = True
#                 elif y >= 120 and x > 200:
#                     print("quit pressed")
#                     can_start = False
#                     code_quit = False
#                     break
#             else:
#                 if(y >= 180):
#                     if(x < 80):
#                         pause_game = not pause_game
#                     elif(x < 160):
#                         og_sleep_time = sleep_time
#                         sleep_time /= 2
#                         if sleep_time <= 0.00125: 
#                             sleep_time = og_sleep_time
#                     elif(x < 240):
#                         og_sleep_time = sleep_time
#                         sleep_time += 0.01
#                         if sleep_time >= 0.05: 
#                             sleep_time = 0.01
#                     else:
#                         lcd.fill(black)
#                         can_start = False

#     time.sleep(sleep_time)

# if ( not GPIO.input(17)):
#     pygame.quit() 
#     import sys
#     sys.exit(0)
pygame.quit() 
import sys
sys.exit(0)
del(pitft)