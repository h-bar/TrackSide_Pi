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
IMG_DIR = ''
VIDEO_FILE = ''
DATA_FILE = ''
data_f = None
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
    'pos': (100, 100),
    'font_size': 55,
    'on': False,
    'online': True,
    'value': 20,
    'unit': 'km/h'
  },
  'rpm': {
    'dev': 'rpm',
    'text': '',
    'pos': (240, 100),
    'font_size': 40,
    'on': False,
    'online': True,
    'value': 20,
    'unit': 'RPM'
  },
  'acce-x': {
    'dev': 'acce',
    'text': 'X: ',
    'pos': (60, 160),
    'font_size': 30,
    'on': True,
    'online': True,
    'value': 20,
    'unit': ''
  },
  'acce-y': {
    'dev': 'acce',
    'text': 'Y: ',
    'pos': (160, 160),
    'font_size': 30,
    'on': True,
    'online': True,
    'value': 20,
    'unit': ''
  },
  'acce-z': {
    'dev': 'acce',
    'text': 'Z: ',
    'pos': (260, 160),
    'font_size': 30,
    'on': True,
    'online': True,
    'value': 20,
    'unit': ''
  },
  'coolant': {
    'dev': 'coolant',
    'text': 'Coolant: ',
    'pos': (80, 200),
    'font_size': 30,
    'on': True,
    'online': True,
    'value': 20,
    'unit': 'F'
  },
  'throttle': {
    'dev': 'throttle',
    'text': 'Throttle: ',
    'pos': (220, 200),
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

    if dev == 'gps':
      text =  str(label['lat']) + ' ' + str(label['lon'])
    else:
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
    setting_labels['gps']['lat'] = round(gps_data['lat'], 1)
    setting_labels['gps']['lon'] = round(gps_data['lon'], 1)
    # print('GPS:', setting_labels['gps']['lat'],  setting_labels['gps']['lon'])

  x, y, z = s.read_acce()
  setting_labels['acce-x']['value'] = round(x, 1)
  setting_labels['acce-y']['value'] = round(y, 1)
  setting_labels['acce-z']['value'] = round(z, 1)
  # print('Acce:', setting_labels['acce']['value'])
  
  # mic = s.read_mic()  
  odb_data = s.read_obd()
  if odb_data['speed'] != None:
    setting_labels['speed']['value'] = round(odb_data['speed'], 1)
    # print('speed:', setting_labels['speed']['value'])
  if odb_data['rpm'] != None:
    setting_labels['rpm']['value'] = round(odb_data['rpm'], 1)
    # print('rpm:', setting_labels['rpm']['value'])
  if odb_data['coolant'] != None:
    setting_labels['coolant']['value'] = round(odb_data['coolant'], 1)
    # print('coolant:', setting_labels['coolant']['value'])
  if odb_data['speed'] != None:
    setting_labels['throttle']['value'] =round( odb_data['throttle'], 1)
    # print('throttle:', setting_labels['throttle']['value'])


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
    timestamp = str(datetime.datetime.now().timestamp())
    rcd_string = timestamp + ';'
    if setting_labels['cam']['on']:
      pygame.image.save(frame, IMG_DIR + '/' +  timestamp + '.BMP')
    if setting_labels['mic']['on']:
      pass
    
    if setting_labels['acce-x']['on']:
      rcd_string += str(setting_labels['acce-x']['value']) + ';'
    if setting_labels['acce-y']['on']:
      rcd_string += str(setting_labels['acce-y']['value']) + ';'
    if setting_labels['acce-z']['on']:
      rcd_string += str(setting_labels['acce-y']['value']) + ';'
    if setting_labels['rpm']['on']:
      rcd_string += str(setting_labels['rpm']['value']) + ';'
    if setting_labels['gps']['on']:
      rcd_string += str(setting_labels['gps']['lat']) + ';' +  str(setting_labels['gps']['lon']) + ';'
    if setting_labels['speed']['on']:
      rcd_string += str(setting_labels['speed']['value']) + ';'
    if setting_labels['coolant']['on']:
      rcd_string += str(setting_labels['coolant']['value']) + ';'
    if setting_labels['throttle']['on']:
      rcd_string += str(setting_labels['throttle']['value']) + ';'
    rcd_string += '\n'
    data_f.write(rcd_string)
  pass

def toggle_recording():
  global recording
  global DATA_FILE
  global IMG_DIR
  global VIDEO_FILE
  global data_f
  recording = not recording
  
  if recording:
    stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    DATA_FILE = RECORDING_ROOT + '/' + stamp + '/' + stamp + '.csv'
    IMG_DIR = RECORDING_ROOT + '/' + stamp + '/imgs'
    VIDEO_FILE = RECORDING_ROOT + '/' + stamp + '/' + stamp + '.mp4'
    
    print(DATA_FILE)
    print(IMG_DIR)
    print(VIDEO_FILE)

    os.makedirs(IMG_DIR)
    data_f = open(DATA_FILE, "w")
    rcd_string = 'timestamp;'
    if setting_labels['acce-x']['on']:
      rcd_string += 'acce-x;'
    if setting_labels['acce-y']['on']:
      rcd_string += 'acce-y;'
    if setting_labels['acce-z']['on']:
      rcd_string += 'acce-z;'
    if setting_labels['rpm']['on']:
      rcd_string += 'rpm;'
    if setting_labels['gps']['on']:
      rcd_string += 'gps-lat;gps-lon;'
    if setting_labels['speed']['on']:
      rcd_string += 'speed;'
    if setting_labels['coolant']['on']:
      rcd_string += 'coolant;'
    if setting_labels['throttle']['on']:
      rcd_string += 'throttle;'
    rcd_string += '\n'
    data_f.write(rcd_string)
  else:
    notification('Saving Recording....')
    try:
      ffmpeg.input(IMG_DIR + '/*.BMP', pattern_type='glob', framerate=47).output(VIDEO_FILE).run()
    except:
      pass
    notification('Recording Saved!')
    data_f.close()
    time.sleep(1)

def end_app():
  s.release()
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

# # Quit Button Setup
# from signal import signal, SIGINT
# from sys import exit

# import RPi.GPIO as GPIO
# GPIO.setmode(GPIO.BCM)

# quit_button = 27
# GPIO.setup(quit_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def _quit():
    # GPIO.cleanup()
    end_app()

# for pin in [17, 22, 23, 27]:
#     GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#     GPIO.add_event_detect(pin, GPIO.FALLING, callback=button_cb, bouncetime=300)

if __name__ == "__main__":
  while True:
    collect_data()
    process_data()
    update_screen()
    handle_events()
    time.sleep(0.01)
