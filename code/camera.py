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


def capture_image(fp, lcd):
    WHITE = (255, 255, 255)
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

def classify_image(cursor, lcd):
    capture_image("user_images/test_im.jpg", lcd)
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
    if (fr.face_encodings(new_face)): 
        new_encoding = fr.face_encodings(new_face)[0]
        matches = fr.compare_faces(old_encodings, new_encoding)
        face_distances = fr.face_distance(old_encodings, new_encoding)
        face_sums = np.sum(face_distances, axis=1)
        best_match = np.argmin(face_sums)
        print(best_match)
        # print(matches)
        # print(best_match)
        name = faces_names[best_match]
        return name 
        # print(name)
    else: 
        return None