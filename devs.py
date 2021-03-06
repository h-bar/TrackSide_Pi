from threading import Thread

import pygame.camera
from pygame.locals import *

import board
import busio
import adafruit_mma8451

import serial #connecting to serial
import pynmea2 #Package for parsing NMEA protocol

import obd
#print(obd.__file__)

import time
import random
import os

from data import dev_readings

def randReading():
  return random.randint(0, 300) / 32.32

class cam:
  VIDEO_SIZE = (480,640)
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
        dev_readings['cam']['frame'] = pygame.transform.rotate(self.frame, 90)
        dev_readings['cam']['new'] = True
    print('Camera Stopped')

class acce:
  def __init__(self):
    print('Initializing Accelerometer...')
    self.i2c = busio.I2C(board.SCL, board.SDA)
    time.sleep(1)
    self.accelerometer = adafruit_mma8451.MMA8451(self.i2c) # Using default address
    self.accelerometer.data_rate = adafruit_mma8451.DATARATE_400HZ #400Hz

  def stop(self):
    print('Stoping Accelerometer...')
    self._running = False

  def release(self):
    print('Releasing Accelerometer...')
    self.i2c.deinit()

  def run(self):
    print('Starting Accelerometer...')
    self._running = True
    while self._running:
      time.sleep(0.1) # normally .5
      try:
        x, y, z = self.accelerometer.acceleration
        # x, y, z = randReading(), randReading(), randReading()
        
        print('++Dev -> X:\t%.3f Y:\t%.3f Z:\t%.3f' %(x, y, z))
        dev_readings['acce']['y'] = x/9.8 # needed adjustment to suit vehicle ref. fram
        dev_readings['acce']['z'] = y/9.8 # converted to g's by factor of 9.8 m/s^2
        dev_readings['acce']['x'] = z/9.8
        dev_readings['acce']['new'] = True
      except Exception as err:
         print("Error reading Accelerometer:", err)
    print('Accelerometer Stopped')

class gps:
  def __init__(self):
    print('Initializing GPS...')
    self.gps = serial.Serial(port = '/dev/ttyS0', baudrate = 9600)

  def stop(self):
    print('Stoping GPS...')
    self._running = False

  def release(self):
    print('Releasing GPS...')
    self.gps.close()

  def run(self):
    print('Starting GPS...')
    self._running = True
    while self._running:
      msg = None
      try:
        line = self.gps.readline().decode("ascii") 
        msg = pynmea2.parse(line)
      except Exception as err:
        print("Error reading GPS:", err)

      if (not msg == None) and (msg.sentence_type == 'GGA'): 
        # print(msg)
        lat = msg.latitude
        lon = msg.longitude
      # if True:
      #   time.sleep(2)
      #   lat, lon = randReading(), randReading()

        print('++Dev -> Lat:\t%.3f Lon:\t%.3f' %(lat, lon))
        dev_readings['gps']['lat'] = lat
        dev_readings['gps']['lon'] = lon
        dev_readings['gps']['new'] = True
    print('GPS Stopped')

class obd_reader:
  def __init__(self):
    print('Initializing OBD...')
    #self.obd = obd.OBD()
    obd.logger.setLevel(obd.logging.DEBUG) # this line is printing obd debugging info
    self.obd = obd.Async()
    self.obd.watch(obd.commands.SPEED)
    self.obd.watch(obd.commands.RPM)
    self.obd.watch(obd.commands.COOLANT_TEMP)
    self.obd.watch(obd.commands.THROTTLE_POS)
    self.obd.start()
    time.sleep(3) # give it time to produce somee data 

  def stop(self):
    print('Stoping OBD...')
    self._running = False

  def release(self):
    print('Releasing OBD...')
    self.obd.stop()
    self.obd.unwatch_all()
    self.obd.close()

  def run(self):
    print('Starting OBD...')
    self._running = True
    while self._running:
      time.sleep(.05)
      try:
        if self.obd.is_connected():
          speed = self.obd.query(obd.commands.SPEED).value.magnitude
          rpm = self.obd.query(obd.commands.RPM).value.magnitude
          coolant = self.obd.query(obd.commands.COOLANT_TEMP).value.magnitude
          throttle = self.obd.query(obd.commands.THROTTLE_POS).value.magnitude
        #if True:
          # time.sleep(4)
          #speed, rpm, coolant, throttle = randReading(), randReading(), randReading(), randReading()

          print('++Dev -> Speed:\t%.3f RPM:\t%.3f Coolant:\t%.3f Throttle:\t%.3f' %(speed, rpm, coolant, throttle))
          dev_readings['speed']['value'] = speed * .621 #converting to mph from Kph
          dev_readings['rpm']['value'] = rpm
          dev_readings['coolant']['value'] = (coolant * 9/5)+32 #Convert to F from C 
          dev_readings['throttle']['value'] = throttle
          dev_readings['speed']['new'] = True
      except Exception as err:
         print("Error reading OBD:", err)
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

    self.devs.append(obd_reader())
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
  try:
    s = sensors()
    s.start()
    input()
    s.stop()
  except:
    s.stop()
