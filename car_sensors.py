import random

# Import packages for acccel
import board
import busio
import adafruit_mma8451
import time

#import packages for GPS
import serial #connecting to serial
import pynmea2 #Package for parsing NMEA protocol

#import packages for obd
import obd

class sensors:
  accelerometer = None
  gps = None
  obd = None

  def __init__(self):
    self.mic_init()
    self.acce_init()
    self.obd_init_async()
    self.gps_init()

  def release(self):
    self.obd.stop()

  def mic_init(self):
    pass

  def acce_init(self):
    i2c = busio.I2C(board.SCL, board.SDA)
    time.sleep(1)
    self.accelerometer = adafruit_mma8451.MMA8451(i2c) # Using default address
    # Set logging rate
    self.accelerometer.data_rate = adafruit_mma8451.DATARATE_400HZ #400Hz
  
  def obd_init(self):
    self.obd = obd.OBD()

  def obd_init_async(self):
    self.obd = obd.Async()
    self.obd.watch(obd.commands.SPEED)
    self.obd.watch(obd.commands.RPM)
    self.obd.watch(obd.commands.SPECOOLANT_TEMPED)
    self.obd.watch(obd.commands.THROTTLE_POS)
    self.obd.start()

  def gps_init(self):
    self.gps = serial.Serial(port = '/dev/ttyS0', baudrate = 9600)

  def read_mic(self):
    pass

  def read_acce(self):
    x, y, z = self.accelerometer.acceleration
    return (x, y, z)

  def read_obd(self):
    speed = None
    rpm = None
    coolant = None
    throttle = None
    try:
      speed = self.obd.query(obd.commands.SPEED).value.magnitude
      rpm = self.obd.query(obd.commands.RPM).value.magnitude
      coolant = self.obd.query(obd.commands.COOLANT_TEMP).value.magnitude
      throttle = self.obd.query(obd.commands.THROTTLE_POS).value.magnitude
    except:
      pass
    
    return {
      'speed': speed,
      'rpm': rpm,
      'coolant': coolant,
      'throttle': throttle,
    }

  def read_gps(self):
    try:
      line = self.gps.readline().decode("ascii") 
      msg = pynmea2.parse(line)
    except:
      return None

    if (msg.sentence_type != 'GGA'): 
      return None
    
    data = {
      'lat': msg.lat,
      'lon': msg.lon
    }

    return data
