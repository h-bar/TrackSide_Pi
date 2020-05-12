disabled = False

dev_readings = {
  'cam': {
    'on': True,
    'frame': None,
    'new': True
  },
  'mic': {
    'on': False
  },
  'acce': {
    'on': True,
    'x': 0,
    'y': 0,
    'z': 0,
    'new': True
  },
  'speed': {
    'on': True,
    'value': 0,
    'new': True
  },
  'rpm': {
    'on': True,
    'value': 0,
    'new': True
  },
  'coolant': {
    'on': True,
    'value': 0,
    'new': True
  },
  'throttle': {
    'on': True,
    'value': 0,
    'new': True
  },
  'gps': {
    'on': True,
    'lat': 0,
    'lon': 0,
    'new': True
  }
}

label_config = {
  'cam': {
    'text': 'Video',
    'pos': (100, 30),
    'font_size': 30,
    'online': True,
    'width': 30
  },
  'mic': {
    'text': 'Audio',
    'pos': (200, 30),
    'font_size': 30,
    'online': False,
    'width': 30
  },
  'acce': {
    'dev': 'acce',
    'text': 'X: %.2f  Y: %.2f  Z: %.2f ',
    'pos': (160, 170),
    'font_size': 30,
    'online': True,
    'width': 120
  },
  'gps': {
    'dev': 'gps',
    'text': '%.8f        %.8f',
    'pos': (160, 70),
    'font_size': 30,
    'online': True,
    'width': 100
  }, 
  'speed': {
    'dev': 'speed',
    'text': '%d km/h',
    'pos': (100, 120),
    'font_size': 55,
    'online': True,
    'width': 60
  },
  'rpm': {
    'dev': 'rpm',
    'text': '%d RPM',
    'pos': (240, 120),
    'font_size': 40,
    'online': True,
    'width': 50
  },
  'coolant': {
    'dev': 'coolant',
    'text': 'Coolant:  %.1fF',
    'pos': (80, 210),
    'font_size': 30,
    'online': True,
    'width': 80
  },
  'throttle': {
    'dev': 'throttle',
    'text': 'Throttle: %d%%',
    'pos': (220, 210),
    'font_size': 30,
    'online': True,
    'width': 80
  },
}
