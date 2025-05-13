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
import numpy as np 
import tensorflow as tf

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Load the saved model
model = tf.keras.models.load_model('mini_xception_model.h5')
# Load the input image
img = cv2.imread('dabke.jpg')
# Convert the image to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# Detect faces in the image
faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# Iterate over the detected faces
for (x, y, w, h) in faces:
    # Extract the face region from the image
    face_roi = gray[y:y+h, x:x+w]
    
    # Preprocess the face region (e.g., resize, normalization)
    face_roi = cv2.resize(face_roi, (48, 48))
    face_roi = face_roi.astype('float32') / 255.0
    face_roi = np.expand_dims(face_roi, axis=0)
    face_roi = np.expand_dims(face_roi, axis=-1)
    
    # Use the loaded model to predict the emotion
    emotion_prediction = model.predict(face_roi)
    emotion_index = np.argmax(emotion_prediction)
    emotion_label = emotion_labels[emotion_index]
    
    print(emotion_labels[emotion_index]) 
    # Draw a rectangle around the face and display the emotion label
    # cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
    # cv2.putText(img, emotion_label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)

