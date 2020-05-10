import time
import json
import signal

FIFO = './sensors'

###############################
#### Acce Init
###############################
print('Initializing Accelerometer...')
import board
import busio
import adafruit_mma8451

i2c = busio.I2C(board.SCL, board.SDA)
time.sleep(1)
accelerometer = adafruit_mma8451.MMA8451(i2c) # Using default address
# Set logging rate
accelerometer.data_rate = adafruit_mma8451.DATARATE_400HZ #400Hz



###############################
#### GPS Init
###############################
print('Initializing GPS...')
import serial #connecting to serial
import pynmea2 #Package for parsing NMEA protocol

gps = serial.Serial(port = '/dev/ttyS0', baudrate = 9600)

###############################
#### OBD Init
###############################
print('Initializing OBD...')
import obd

# _obd = obd.OBD()
_obd = obd.Async()
_obd.watch(obd.commands.SPEED)
_obd.watch(obd.commands.RPM)
_obd.watch(obd.commands.COOLANT_TEMP)
_obd.watch(obd.commands.THROTTLE_POS)
_obd.start()

###############################
#### FIFO Init
###############################
fifo = open(FIFO, 'w')


def signal_handler(sig, frame):
  _obd.stop()
  _obd.unwatch_all()
  i2c.deinit()
  gps.close()
  print('All connections released!')
  exit(0)

signal.signal(signal.SIGINT, signal_handler)


data = {
  'time': 0,
  'acce-x': 0,
  'acce-y': 0,
  'acce-z': 0,
  'speed': 0,
  'rpm': 0,
  'coolant': 0,
  'throttle': 0,
  'gps-lon': 0,
  'gps-lat': 0
}

print("Piping data into FIFO", FIFO)
while True:
  ###############################
  #### READ Acce
  ###############################
  data['acce-x'], data['acce-y'], data['acce-z'] = accelerometer.acceleration

  ###############################
  #### READ OBD
  ###############################
  try:
    data['speed'] = _obd.query(obd.commands.SPEED).value.magnitude
    data['rpm'] = _obd.query(obd.commands.RPM).value.magnitude
    data['coolant'] = _obd.query(obd.commands.COOLANT_TEMP).value.magnitude
    data['throttle'] = _obd.query(obd.commands.THROTTLE_POS).value.magnitude
  except:
    pass


  ###############################
  #### READ GPS
  ###############################
  msg = None
  try:
    line = gps.readline().decode("ascii") 
    msg = pynmea2.parse(line)
  except:
    pass

  if (not msg == None) and (msg.sentence_type == 'GGA'): 
    data['gps-lat'] = msg.latitude
    data['gps-lon'] = msg.longitude

  data['time'] = time.time()
  # print(data)
  data_str = json.dumps(data)
  # print(data_str)
  fifo.write(data_str)
  fifo.flush()
  time.sleep(0.5)