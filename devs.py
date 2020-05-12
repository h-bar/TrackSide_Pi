from threading import Thread

import pygame.camera
from pygame.locals import *

# import board
# import busio
# import adafruit_mma8451

# import serial #connecting to serial
# import pynmea2 #Package for parsing NMEA protocol

import time
import random
import os

from data import dev_readings

def randReading():
  return random.randint(0, 300) / 32.32

class cam:
  VIDEO_SIZE = (640,480)
  CAM_DEV = '/dev/video0'

  def __init__(self):
    print('Initializing Camera...')
    pygame.camera.init()
    self.cam = pygame.camera.Camera(self.CAM_DEV, self.VIDEO_SIZE)
    self.cam.start()
    self.frame = pygame.surface.Surface(self.VIDEO_SIZE, 0, None)

  def stop(self):
    print('Stoping Camera...')
    self._running = False

  def release(self):
    print('Releasing Camera...')
    self.cam.stop()

  def run(self):
    print('Starting Camera...')
    self._running = True
    while self._running:
      time.sleep(0.04)
      if self.cam.query_image():
        # print('Got a frame')
        self.frame = self.cam.get_image(self.frame)
        dev_readings['cam']['frame'] = self.frame
        dev_readings['cam']['new'] = True
    print('Camera Stopped')

class acce:
  def __init__(self):
    print('Initializing Accelerometer...')
    # self.i2c = busio.I2C(board.SCL, board.SDA)
    # time.sleep(1)
    # self.accelerometer = adafruit_mma8451.MMA8451(self.i2c) # Using default address
    # self.accelerometer.data_rate = adafruit_mma8451.DATARATE_400HZ #400Hz

  def stop(self):
    print('Stoping Accelerometer...')
    self._running = False

  def release(self):
    print('Releasing Accelerometer...')
    # self.i2c.deinit()

  def run(self):
    print('Starting Accelerometer...')
    self._running = True
    while self._running:
      time.sleep(1)

      # x, y, z = self.accelerometer.acceleration
      x, y, z = randReading(), randReading(), randReading()
      
      print('++Dev -> X:\t%.3f Y:\t%.3f Z:\t%.3f' %(x, y, z))
      dev_readings['acce']['x'] = x
      dev_readings['acce']['y'] = y
      dev_readings['acce']['z'] = z
      dev_readings['acce']['new'] = True
    print('Accelerometer Stopped')

class gps:
  def __init__(self):
    print('Initializing GPS...')
    # self.gps = serial.Serial(port = '/dev/ttyS0', baudrate = 9600)

  def stop(self):
    print('Stoping GPS...')
    self._running = False

  def release(self):
    print('Releasing GPS...')
    # gps.close()

  def run(self):
    print('Starting GPS...')
    self._running = True
    while self._running:
      # msg = None
      # try:
      #   line = gps.readline().decode("ascii") 
      #   msg = pynmea2.parse(line)
      # except:
      #   pass

      # if (not msg == None) and (msg.sentence_type == 'GGA'): 
      #   lat = msg.latitude
      #   lon = msg.longitude
      if True:
        time.sleep(2)
        lat, lon = randReading(), randReading()

        print('++Dev -> Lat:\t%.3f Lon:\t%.3f' %(lat, lon))
        dev_readings['gps']['lat'] = lat
        dev_readings['gps']['lon'] = lon
        dev_readings['gps']['new'] = True
    print('GPS Stopped')

class obd:
  def __init__(self):
    print('Initializing GPS...')
    # self.obd = obd.OBD()

    # # self.obd = obd.Async()
    # # self.obd.watch(obd.commands.SPEED)
    # # self.obd.watch(obd.commands.RPM)
    # # self.obd.watch(obd.commands.COOLANT_TEMP)
    # # self.obd.watch(obd.commands.THROTTLE_POS)
    # # self.obd.start()

  def stop(self):
    print('Stoping OBD...')
    self._running = False

  def release(self):
    print('Releasing OBD...')
    # # self.obd.stop()
    # # self.obd.unwatch_all()
    # obd.close()

  def run(self):
    print('Starting OBD...')
    self._running = True
    while self._running:
      # if self.obd.is_connected():
      #   speed = self.obd.query(obd.commands.SPEED).value.magnitude
      #   rpm = self.obd.query(obd.commands.RPM).value.magnitude
      #   coolant = self.obd.query(obd.commands.COOLANT_TEMP).value.magnitude
      #   throttle = self.obd.query(obd.commands.THROTTLE_POS).value.magnitude
      if True:
        time.sleep(4)
        speed, rpm, coolant, throttle = randReading(), randReading(), randReading(), randReading()

        print('++Dev -> Speed:\t%.3f RPM:\t%.3f Coolant:\t%.3f Throttle:\t%.3f' %(speed, rpm, coolant, throttle))
        dev_readings['speed']['value'] = speed
        dev_readings['rpm']['value'] = rpm
        dev_readings['coolant']['value'] = coolant
        dev_readings['throttle']['value'] = throttle
        dev_readings['speed']['new'] = True
    print('OBD Stopped')

class sensors():
  def __init__(self):  
    self.threads = []
    self.devs = []

    self.devs.append(cam())
    self.threads.append(Thread(target=self.devs[-1].run))

    self.devs.append(acce())
    self.threads.append(Thread(target=self.devs[-1].run))

    self.devs.append(gps())
    self.threads.append(Thread(target=self.devs[-1].run))

    self.devs.append(obd())
    self.threads.append(Thread(target=self.devs[-1].run))


  def start(self):
    for t in self.threads:
      t.start()

  def stop(self):
    for t in self.devs:
      t.stop()
    time.sleep(5)
    for t in self.devs:
      t.release()
    
if __name__ == "__main__":
  s = sensors()
  s.start()
  input()
  s.stop()