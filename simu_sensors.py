import time
import json
import signal
import random

FIFO = './sensors'

###############################
#### FIFO Init
###############################
fifo = open(FIFO, 'w')

def randData():
  return random.random()*10

def signal_handler(sig, frame):
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
  data['acce-x'], data['acce-y'], data['acce-z'] = (randData(), randData(), randData())

  ###############################
  #### READ OBD
  ###############################
  try:
    data['speed'] = randData()
    data['rpm'] = randData()
    data['coolant'] = randData()
    data['throttle'] = randData()
  except:
    pass


  ###############################
  #### READ GPS
  ###############################
  data['gps-lat'] = randData()
  data['gps-lon'] = randData()

  data['time'] = time.time()
  # print(data)
  data_str = json.dumps(data)
  # print(data_str)
  fifo.write(data_str)
  fifo.flush()
  time.sleep(0.05)