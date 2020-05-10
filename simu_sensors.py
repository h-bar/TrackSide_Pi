import random

class sensors:
  accelerometer = None
  gps = None
  obd = None

  def __init__(self):
    self.mic_init()
    self.acce_init()
    self.obd_init()
    self.gps_init()

  def release(self):
    pass

  def mic_init(self):
    pass

  def acce_init(self):
    pass
  
  def obd_init(self):
    pass

  def gps_init(self):
    pass

  def read_mic(self):
    pass

  def read_acce(self):
    return (
      random.randint(0, 40) / 3.534,
      random.randint(0, 40) / 3.534,
      random.randint(0, 40) / 3.534
    )
    
  def read_obd(self):    
    return {
      'speed': random.randint(0, 40) / 3.534,
      'rpm': random.randint(0, 40) / 3.534,
      'coolant': random.randint(0, 40) / 3.534,
      'throttle': random.randint(0, 40) / 3.534,
    }

  def read_gps(self):
    return {
      'lat': str(random.randint(0, 40) / 3.534),
      'lon': str(random.randint(0, 40) / 3.534),
    }
