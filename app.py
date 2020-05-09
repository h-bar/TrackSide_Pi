import time
import datetime
import sys
import pygame
import pygame.camera
from pygame.locals import *
import os
import random
import ffmpeg

# from car_sensors import sensors
from simu_sensors import sensors

# os.putenv('SDL_VIDEODRIVER', 'fbcon')   # Display on piTFT#
# os.putenv('SDL_FBDEV', '/dev/fb1')
# os.putenv('SDL_MOUSEDRV', 'TSLIB')     # Track mouse clicks on piTFT
# os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')


WHITE = 255, 255, 255
BLACK = 0,0,0
RED = 255, 0, 0
GREEN = 0, 255, 0
GREY = 128,128,128

SCREEN_SIZE = (320,240)
VIDEO_SIZE = (640,480)
RECORDING_ROOT = './rcd'
RECORDING_DIR = ''
VIDEO_DIR = 'video'
DATA_FILE = 'data.csv'
CAM_DEV = '/dev/video0'

pygame.init()
# pygame.mouse.set_visible(False)
pygame.camera.init()

screen = pygame.display.set_mode(SCREEN_SIZE)
cam = pygame.camera.Camera(CAM_DEV, VIDEO_SIZE)
frame = pygame.surface.Surface(VIDEO_SIZE, 0, screen)
  
s = sensors()
cam.start()


setting_labels = {
  'cam': {
    'dev': 'cam',
    'text': 'Video',
    'pos': (60, 40),
    'font_size': 30,
    'on': False,
    'on': False,
    'online': True,
    'value': '',
    'unit': ''
  },
  'mic': {
    'dev': 'mic',
    'text': 'Audio',
    'pos': (160, 40),
    'font_size': 30,
    'on': False,
    'online': True,
    'value': '',
    'unit': ''
  },
  'gps': {
    'dev': 'gps',
    'text': 'GPS',
    'pos': (260, 40),
    'font_size': 30,
    'on': False,
    'online': True,
    'value': '',
    'unit': '',
    'lat': 0,
    'lon': 0
  }, 
  'speed': {
    'dev': 'speed',
    'text': '',
    'pos': (100, 105),
    'font_size': 55,
    'on': False,
    'online': True,
    'value': 20,
    'unit': 'km/h'
  },
  'acce': {
    'dev': 'acce',
    'text': '',
    'pos': (240, 85),
    'font_size': 35,
    'on': True,
    'online': True,
    'value': 20,
    'unit': 'm/s^2'
  },
  'rpm': {
    'dev': 'rpm',
    'text': '',
    'pos': (240, 120),
    'font_size': 35,
    'on': False,
    'online': True,
    'value': 20,
    'unit': 'RPM'
  },
  'coolant': {
    'dev': 'coolant',
    'text': 'Coolant: ',
    'pos': (80, 160),
    'font_size': 30,
    'on': True,
    'online': True,
    'value': 20,
    'unit': 'F'
  },
  'throttle': {
    'dev': 'throttle',
    'text': 'Throttle: ',
    'pos': (220, 160),
    'font_size': 30,
    'on': False,
    'online': True,
    'value': 20,
    'unit': '%'
  },
}

recordingCircle = {
    'color': RED,
    'pos': (15, 15),
    'r': 10
}

from enum import Enum
class Views(Enum):
  Video = 1
  Setting = 2

current_view = Views.Setting
recording = False

def draw_video_view():
  screen.blit(pygame.transform.scale(frame, SCREEN_SIZE), (0,0))

def draw_setting_view():
  for dev in setting_labels:
    label = setting_labels[dev]
    text = label['text'] + str(label['value']) + label['unit']

    text_color = WHITE
    if not label['online']:
      text_color = GREY
    elif label['on']:
      text_color = GREEN

    label_surface = pygame.font.Font(None, label['font_size']).render(text, True, text_color)

    rect = label_surface.get_rect(center=label['pos'])
    screen.blit(label_surface, rect)

def notification(text):
  screen.fill(BLACK)
  label_surface = pygame.font.Font(None, 40).render(text, True, WHITE)

  rect = label_surface.get_rect(center=(SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2))
  screen.blit(label_surface, rect)
  pygame.display.flip()
  pass

def collect_data():
  global frame
  global setting_labels
  if cam.query_image():
    frame = cam.get_image(frame)

  gps_data = s.read_gps()
  if gps_data != None:
    setting_labels['gps']['lat'] = gps_data['lat']
    setting_labels['gps']['lon'] = gps_data['lon']
    print('GPS:', setting_labels['gps']['lat'],  setting_labels['gps']['lon'])

  acce_data = s.read_acce()
  setting_labels['acce']['value'] = acce_data
  print('Acce:', setting_labels['acce']['value'])
  
  # mic = s.read_mic()  
  odb_data = s.read_obd()
  if odb_data['speed'] != None:
    setting_labels['speed']['value'] = odb_data['speed']
    print('speed:', setting_labels['speed']['value'])
  if odb_data['rpm'] != None:
    setting_labels['rpm']['value'] = odb_data['rpm']
    print('rpm:', setting_labels['rpm']['value'])
  if odb_data['coolant'] != None:
    setting_labels['coolant']['value'] = odb_data['coolant']
    print('coolant:', setting_labels['coolant']['value'])
  if odb_data['speed'] != None:
    setting_labels['speed']['value'] = odb_data['throttle']
    print('speed:', setting_labels['speed']['value'])


def handle_events():
  global current_view
  events = pygame.event.get()
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
    elif recording == False and event.type == pygame.MOUSEBUTTONUP:
      pos = pygame.mouse.get_pos()
      for dev in setting_labels:
        label = setting_labels[dev]
        if pos[0] > label['pos'][0] - (label['font_size']):
          if pos[0] < label['pos'][0] + (label['font_size']):
            if pos[1] > label['pos'][1]- (label['font_size'] / 2):
              if pos[1] < label['pos'][1] + (label['font_size'] / 2):
                  label['on'] = not label['on']
                  break


def update_screen():
  screen.fill(BLACK)
  if current_view == Views.Video:
    draw_video_view()
  elif current_view == Views.Setting:
    draw_setting_view()

  if recording:
    pygame.draw.circle(screen, recordingCircle['color'], recordingCircle['pos'], recordingCircle['r'])
  
  pygame.display.flip()

def process_data():
  if recording:
    timestamp = str(datetime.datetime.now())
    if setting_labels['cam']['on']:
      pygame.image.save(frame, RECORDING_DIR + '/' + VIDEO_DIR + '/' +  timestamp + '.BMP')
  
  pass

def toggle_recording():
  global recording
  global RECORDING_DIR
  recording = not recording
  stamp = str(datetime.datetime.now())
  if recording:
    RECORDING_DIR = RECORDING_ROOT + '/' + stamp
    os.makedirs(RECORDING_DIR)
    os.makedirs(RECORDING_DIR+'/'+VIDEO_DIR)   
    print("Recording start, saving to ", RECORDING_DIR)
  else:
    notification('Saving Recording....')
    try:
      ffmpeg.input(RECORDING_DIR+'/'+VIDEO_DIR + '/*.BMP', pattern_type='glob', framerate=14).output(RECORDING_DIR+'/'+VIDEO_DIR + '/' + stamp + '.mp4').run()
    except:
      pass
    notification('Recording Saved!')
    time.sleep(1)
def end_app():
  s.release()
  exit(0)


# # Quit Button Setup
# from signal import signal, SIGINT
# from sys import exit

# import RPi.GPIO as GPIO
# GPIO.setmode(GPIO.BCM)

# quit_button = 27
# GPIO.setup(quit_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def _quit():
    # GPIO.cleanup()
    exit(0)

def button_cb(channel):
  global current_view
  if channel == 17:
    current_view = Views.Video
  elif channel == 22:
    current_view = Views.Setting
  elif channel == 23:
    toggle_recording()
  elif channel == 27:
    _quit()

# for pin in [17, 22, 23, 27]:
#     GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#     GPIO.add_event_detect(pin, GPIO.FALLING, callback=button_cb, bouncetime=300)

if __name__ == "__main__":
  while True:
    collect_data()
    process_data()
    update_screen()
    handle_events()
    time.sleep(0.05)
