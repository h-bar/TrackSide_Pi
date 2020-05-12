import time
import pygame
import datetime
import os 
import csv
import subprocess
import data
from devs import sensors

WHITE = 255, 255, 255
BLACK = 0,0,0
RED = 255, 0, 0
GREEN = 0, 255, 0
GREY = 128,128,128

SCREEN_SIZE = (320,240)

IDLE_VIEW = 0
CAM_VIEW = 1
DATA_VIEW = 2


os.putenv('SDL_VIDEODRIVER', 'fbcon')   # Display on piTFT#
os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDRV', 'TSLIB')     # Track mouse clicks on piTFT
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

for pin in [17, 22, 23, 27]:
  GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def handle_buttons():
  for btn in [17, 22, 23, 27]:
    if GPIO.input(btn) == GPIO.LOW:
      button_cb(btn)
  pass

def end_app():
  global r
  if not r == None:
    toggle_recording()

  data.disabled = True
  prompt('Existing...', 0)
  s.stop()
  GPIO.cleanup()
  exit(0)


global s
global r
global view

class recorder():
  root = './static/rcd'
  video_rate = 400
  data_rate = 1000 
  def __init__(self):
    stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    rcd_dir = os.path.join(self.root, stamp)

    self.img_dir = os.path.join(rcd_dir, 'img/')
    os.makedirs(self.img_dir, exist_ok=True)
    
    self.video_filename = os.path.join(rcd_dir, stamp + '.mp4')
    
    data_filename = os.path.join(rcd_dir, stamp + '.csv')
    self.data_file = open(data_filename, 'w+')
    sensor_data = self.collect_data()
    self.data_writer =  csv.DictWriter(self.data_file, fieldnames=list(sensor_data.keys()))
    self.data_writer.writeheader()
    self.counter = 0
    self.image_counter = 0
    self.rcd_time = time.time()

  def log_data(self):
    if not self.data_file.closed and self.counter % self.data_rate == 0:
      self.data_writer.writerow(self.collect_data())
    if data.dev_readings['cam']['on'] and self.counter % self.video_rate == 0:
      pygame.image.save(data.dev_readings['cam']['frame'], os.path.join(self.img_dir, str(self.image_counter) + '.BMP'))
      self.image_counter += 1
    self.counter += 1

  def collect_data(self):
    sensor_data = {} 
    sensor_data['timestamp'] = time.time()
    if data.dev_readings['acce']['on']:
      sensor_data['x'] = data.dev_readings['acce']['x']
      sensor_data['y'] = data.dev_readings['acce']['y']
      sensor_data['z'] = data.dev_readings['acce']['z']
    if data.dev_readings['gps']['on']:
      sensor_data['lat'] = data.dev_readings['gps']['lat']
      sensor_data['lon'] = data.dev_readings['gps']['lon']
    if data.dev_readings['rpm']['on']:
      sensor_data['rpm'] = data.dev_readings['rpm']['value']
    if data.dev_readings['speed']['on']:
      sensor_data['speed'] = data.dev_readings['speed']['value']
    if data.dev_readings['coolant']['on']:
      sensor_data['coolant'] = data.dev_readings['coolant']['value']
    if data.dev_readings['throttle']['on']:
      sensor_data['throttle'] = data.dev_readings['throttle']['value']
    return sensor_data

  def stop(self):
    self.data_file.close()
    if data.dev_readings['cam']['on']:
      self.rcd_time = time.time() - self.rcd_time
      fps = int(self.image_counter / self.rcd_time * 0.75)
      print('Saving video of fps %d'%fps)
      data.disabled = True
      prompt('Saving Video...', 0)
      subprocess.run(['ffmpeg', '-r', str(fps), '-i', self.img_dir + '/%d.BMP', '-vcodec','libx264', '-pix_fmt', 'yuv420p', self.video_filename]) 
      data.disabled = False
      prompt('Video saved!', 2)

def prompt(text, timeout):
  global view
  _view = view
  view = IDLE_VIEW
  screen.fill(BLACK)
  label_surface = pygame.font.Font(None, 40).render(text, True, WHITE)
  rect = label_surface.get_rect(center=(SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2))
  screen.blit(label_surface, rect)
  pygame.display.flip()
  time.sleep(timeout)
  view = _view

def toggle_recording():
  global r
  data.dev_readings['speed']['new'] = True

  if r == None:
    print('Start recording...')
    r = recorder()
  else:
    print('Stop recording...')
    r.stop()
    r = None

def button_cb(channel):
  global view
  if not data.disabled:
    if channel == 17:
      view = CAM_VIEW
    elif channel == 22:
      view = DATA_VIEW
    elif channel == 23:
      toggle_recording()
    elif channel == 27:
      end_app()


def render_camera_view(screen):
  if data.dev_readings['cam']['new']:
    frame = data.dev_readings['cam']['frame']
    screen.fill(BLACK)
    screen.blit(pygame.transform.scale(frame, SCREEN_SIZE), (0,0))
    pygame.display.flip()
    data.dev_readings['cam']['new'] = False

def make_label(label, text, status):
  text_color = WHITE
  if not label['online']:
    text_color = GREY
  elif status:
    text_color = GREEN

  label_surface = pygame.font.Font(None, label['font_size']).render(text, True, text_color)
  rect = label_surface.get_rect(center=label['pos'])
  return label_surface, rect

def render_data_view(screen):
  update = False
  for reading in data.dev_readings:
    if not reading == 'cam' and not reading == 'mic' and data.dev_readings[reading]['new']:
      update = True
  
  if not update:
    return

  print('--App -> X:\t%.3f Y:\t%.3f Z:\t%.3f' %(data.dev_readings['acce']['x'], data.dev_readings['acce']['y'], data.dev_readings['acce']['z']))
  print('--App -> Lat:\t%.3f Lon:\t%.3f' %(data.dev_readings['gps']['lat'], data.dev_readings['gps']['lon']))
  print('--App -> Speed:\t%.3f RPM:\t%.3f Coolant:\t%.3f Throttle:\t%.3f' %(data.dev_readings['speed']['value'], data.dev_readings['rpm']['value'], data.dev_readings['coolant']['value'], data.dev_readings['throttle']['value']))

  screen.fill(BLACK)
  
  dev = 'cam'
  label = data.label_config[dev]
  text = label['text']
  status = data.dev_readings[dev]['on']
  label_surface, rect = make_label(data.label_config[dev], text, status)
  screen.blit(label_surface, rect)

  dev = 'mic'
  label = data.label_config[dev]
  text = label['text']
  status = data.dev_readings[dev]['on']
  label_surface, rect = make_label(data.label_config[dev], text, status)
  screen.blit(label_surface, rect)

  dev = 'gps'
  label = data.label_config[dev]
  text = label['text']%(data.dev_readings[dev]['lat'], data.dev_readings[dev]['lon'])
  status = data.dev_readings[dev]['on']
  label_surface, rect = make_label(data.label_config[dev], text, status)
  screen.blit(label_surface, rect)

  dev = 'acce'
  label = data.label_config[dev]
  text = label['text']%(data.dev_readings[dev]['x'], data.dev_readings[dev]['y'], data.dev_readings[dev]['z'])
  status = data.dev_readings[dev]['on']
  label_surface, rect = make_label(data.label_config[dev], text, status)
  screen.blit(label_surface, rect)
  

  dev = 'speed'
  label = data.label_config[dev]
  text = label['text']%(data.dev_readings[dev]['value'])
  status = data.dev_readings[dev]['on']
  label_surface, rect = make_label(data.label_config[dev], text, status)
  screen.blit(label_surface, rect)
  
  dev = 'rpm'
  label = data.label_config[dev]
  text = label['text']%(data.dev_readings[dev]['value'])
  status = data.dev_readings[dev]['on']
  label_surface, rect = make_label(data.label_config[dev], text, status)
  screen.blit(label_surface, rect)
  
  
  dev = 'coolant'
  label = data.label_config[dev]
  text = label['text']%(data.dev_readings[dev]['value'])
  status = data.dev_readings[dev]['on']
  label_surface, rect = make_label(data.label_config[dev], text, status)
  screen.blit(label_surface, rect)
  
  dev = 'throttle'
  label = data.label_config[dev]
  text = label['text']%(data.dev_readings[dev]['value'])
  status = data.dev_readings[dev]['on']
  label_surface, rect = make_label(data.label_config[dev], text, status)
  screen.blit(label_surface, rect)
  
  
  pygame.display.flip()
  for reading in data.dev_readings:
    data.dev_readings[reading]['new'] = False
  

def update_screen(screen):
  global view
  global r

  if view == IDLE_VIEW:
    pass
  elif view == CAM_VIEW:
    render_camera_view(screen)
  elif view == DATA_VIEW:
    render_data_view(screen)

  if not r == None:
    pygame.draw.circle(screen, RED, (20, 20), 10)
    pygame.display.flip()

def handle_events():
  global view
  global r
  events = pygame.event.get()
  handle_buttons()
  for event in events:
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_v:
        button_cb(17)
      elif event.key == pygame.K_s:
        button_cb(22)
      elif event.key == pygame.K_r:
        button_cb(23)
      elif event.key == pygame.K_q:
        button_cb(27)
    elif r == None and view == DATA_VIEW and event.type == pygame.MOUSEBUTTONUP:
      pos = pygame.mouse.get_pos()
      for dev in data.label_config:
        label = data.label_config[dev]
        if pos[0] > label['pos'][0] - (label['width']):
          if pos[0] < label['pos'][0] + (label['width']):
            if pos[1] > label['pos'][1]- (label['font_size'] / 2):
              if pos[1] < label['pos'][1] + (label['font_size'] / 2):
                  data.dev_readings[dev]['on'] = not data.dev_readings[dev]['on']
                  data.dev_readings['speed']['new'] = True
                  break

if __name__ == "__main__":  
  global s
  global view
  global r
  
  

  try:
    pygame.init()
    pygame.mouse.set_visible(False)
    screen = pygame.display.set_mode(SCREEN_SIZE)

    s = sensors()
    r = None
    view = DATA_VIEW
    # view = CAM_VIEW

    s.start()
    while True:
      update_screen(screen)
      handle_events()
      if not r == None:
        r.log_data()
  except Exception as e:
    print('###############')
    print('Error:', e)
    print('###############')

  end_app()