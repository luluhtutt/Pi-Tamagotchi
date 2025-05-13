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

def display_tama_files(path, x, y, rescale, lcd):
  tama_im = pygame.image.load(path)
  tama_icon = pygame.transform.scale(tama_im, rescale)
  tama_rect_icon = tama_icon.get_rect()
  tama_rect_icon.x = x
  tama_rect_icon.y = y
  lcd.blit(tama_icon, tama_rect_icon)

def feed(cursor, lcd, img_path): 
  start_time = time.time() 
  end_time = start_time + 30 

  while time.time() < end_time:
    display_tama_files(img_path, 240, 120, (60, 60), lcd)
    pygame.display.update() 
    time.sleep(0.1)

  return


def health(cursor, lcd):
  pass 


def hunger(cursor, lcd):
  pass 