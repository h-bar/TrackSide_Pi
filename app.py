
import time
import datetime
import sys
import pygame
from pygame.locals import *
import os
import random

from car_sensors import sensors

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
pygame.init()
s = sensors()
# pygame.mouse.set_visible(False)

screen = pygame.display.set_mode(SCREEN_SIZE)

setting_labels = {
  'cam': {
    'dev': 'cam',
    'text': 'Video',
    'pos': (60, 40),
    'font_size': 30,
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
    'online': False,
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
    'unit': ''
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
    'online': False,
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
  'oil': {
    'dev': 'oil',
    'text': 'Oil: ',
    'pos': (220, 160),
    'font_size': 30,
    'on': False,
    'online': True,
    'value': 20,
    'unit': 'F'
  },
  'throttle': {
    'dev': 'throttle',
    'text': 'Throttle: ',
    'pos': (80, 200),
    'font_size': 30,
    'on': False,
    'online': True,
    'value': 20,
    'unit': '%'
  },
  'brake': {
    'dev': 'brake',
    'text': 'Brake: ',
    'pos': (220, 200),
    'font_size': 30,
    'on': False,
    'online': True,
    'value': 20,
    'unit': 'bar'
  },
}

from enum import Enum
class Views(Enum):
  Video = 1
  Setting = 2
  Map = 3

current_view = Views.Video
recording = True

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

def draw_map_view():
  pass

def collect_data():
  global frame
  global setting_labels

  cam_data = s.read_camara()
  # mic = s.read_mic()  
  odb_data = s.read_obd()
  acce_data = s.read_acce()
  # gps_data = s.read_gps()

  if cam_data != None:
    frame = cam_data
  setting_labels['acce']['value'] = acce_data
  setting_labels['rpm']['value'] = odb_data['rpm']
  setting_labels['coolant']['value'] = odb_data['coolant']
  setting_labels['oil']['value'] = odb_data['oil']
  setting_labels['throttle']['value'] = odb_data['throttle']
  setting_labels['brake']['value'] = odb_data['brake']


def handle_events():
  global current_view
  events = pygame.event.get()
  for event in events:
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_v:
        current_view = Views.Video
      elif event.key == pygame.K_s:
        current_view = Views.Setting
      elif event.key == pygame.K_q:
        _quit()
    elif event.type == pygame.MOUSEBUTTONUP:
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
  elif current_view == Views.Map:
    draw_map_view()
  pygame.display.flip()

def process_data():
  # if recording:
  #   timestamp = str(datetime.datetime.now().timestamp())
  #   if setting_labels['cam']['on']:
  #     pygame.image.save(frame, './recording/' + timestamp + '.BMP')
  
  pass

def _quit():
  s.release()
  quit(0)

def loop():
  timer = time.time()

  while True:
    collect_data()
    process_data()
    timer = time.time()
    update_screen()
    handle_events()
    time.sleep(0.05)

loop()