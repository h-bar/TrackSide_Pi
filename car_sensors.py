import random

class sensors:
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