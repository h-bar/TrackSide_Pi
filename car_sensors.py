
import pygame
import pygame.camera
from pygame.locals import *
import random

import cv2
import numpy as np

class sensors:
  VIDEO_SIZE = (640,480)
  # cam_dev = '/dev/video0'
  # cam = None

  camera = cv2.VideoCapture(0)

  def __init__(self):
    self.cam_init()
    self.mic_init()
    self.acce_init()
    self.obd_init()
    self.gps_init()

  def release(self):
    self.camera.release()
    
  def cam_init(self):
   pass

  def mic_init(self):
    pass

  def acce_init(self):
    pass
  
  def obd_init(self):
    pass

  def gps_init(self):
    pass





  def read_camara(self):
    ret, frame = self.camera.read()
    if ret==True: 
      frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      frame = np.rot90(frame)
      return pygame.surfarray.make_surface(frame)
    return None

  def read_mic(self):
    pass

  def read_acce(self):
    acce = random.randint(0, 50)

    return acce

  def read_obd(self):
    speed = random.randint(0, 50)
    rpm = random.randint(0, 50)
    coolant = random.randint(0, 50)
    oil = random.randint(0, 50)
    throttle = random.randint(0, 50)
    brake = random.randint(0, 50)

    return {
      'speed': speed,
      'rpm': rpm,
      'coolant': coolant,
      'oil': oil,
      'throttle': throttle,
      'brake': brake,
    }

  def read_gps(self):
    return (random.randint(0, 50), random.randint(0, 50))