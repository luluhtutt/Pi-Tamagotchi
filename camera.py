import pygame, pigame
from pygame.locals import * 
import os 
import time
import RPi.GPIO as GPIO
import subprocess
import picamera
import cv2 
import sqlite3
import dlib as d
import face_recognition as fr
import numpy as np 

os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDRV', 'dummy')
os.putenv('SDL_MOUSEDEV', '/dev/null')
os.putenv('DISPLAY', '')

connection = sqlite3.connect("user.db")

cursor = connection.cursor()

def capture_image(fp): 
    camera = picamera.PiCamera()

    camera.start_preview()
    camera.resolution = (640, 480)

    pygame.init() 
    pygame.mouse.set_visible(False)

    pitft = pigame.PiTft()
    size = width, height = 320,240
    lcd = pygame.display.set_mode((width, height))
    lcd.fill((0,0,0))
    pygame.display.update()

    WHITE = ((255, 255, 255))

    font_cam = pygame.font.Font(None, 30)
    font_small = pygame.font.Font(None, 30)

    # Create a button to capture the frame
    capture_button = {"SMILE FOR THE CAMERA:)" : (160, 120)}
    for k,v in capture_button.items():
        text_surface = font_cam.render('%s'%k, True, WHITE)
        rect = text_surface.get_rect(center=v) 
        lcd.blit(text_surface, rect)

    pygame.display.update()
    click = True 
    count = 1
    # Wait for the user to click the button
    while click: 
        pygame.display.update()
        pitft.update()
        for event in pygame.event.get(): 
            if(event.type is MOUSEBUTTONDOWN): 
                x,y = pygame.mouse.get_pos()  
                if x > 0 and y > 0: 
                    print("button press")
                    for i in range(5, 0, -1): 
                        time.sleep(1)
                        pygame.draw.rect(lcd, (0,0,0), pygame.Rect(60, 40, 150, 50))
                        pygame.display.update()
                        k = str(i)
                        text_surface_2 = font_small.render('%s'%k, True, WHITE)
                        rect_2 = text_surface_2.get_rect(center=(120, 60)) 
                        lcd.blit(text_surface_2, rect_2)
                        pygame.display.update() 
                    count += 1
                    camera.capture(fp)
                    camera.stop_preview()
                    click = False

    # pygame.quit() 
    # import sys
    # sys.exit(0)
    # del(pitft)

def classify_image():
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
    cursor.execute(""" select Name from User;""")
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

    print(name)
    pygame.quit() 
    import sys
    sys.exit(0)
    del(pitft)

    # new_encoding = fr.face_encodings(new_face)[0]
    # old_encoding = fr.face_encodings(old_face)[0]

    # matches = fr.compare_faces(new_encoding, old_encoding)
    # face_distances = fr.face_distance()

classify_image()

# capture_image()
connection.commit()
connection.close()
