# Quit Button Setup
from signal import signal, SIGINT
from sys import exit

# import RPi.GPIO as GPIO
# GPIO.setmode(GPIO.BCM)

# quit_button = 17
# GPIO.setup(quit_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def _quit():
    # GPIO.cleanup()
    exit(0)

def quit_cb(channel):
    _quit()

def quit_sig(signal_received, frame):
    _quit()

# GPIO.add_event_detect(quit_button, GPIO.FALLING, callback=quit_cb, bouncetime=300)
signal(SIGINT, quit_sig)


# Actual code starts from here
import time
import sys
import pygame
import pygame.camera
from pygame.locals import *
import os

# os.putenv('SDL_VIDEODRIVER', 'fbcon')   # Display on piTFT#
# os.putenv('SDL_FBDEV', '/dev/fb1')
# os.putenv('SDL_MOUSEDRV', 'TSLIB')     # Track mouse clicks on piTFT
# os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')


WHITE = 255, 255, 255
BLACK = 0,0,0
RED = 255, 0, 0
GREEN = 0, 255, 0
GREY = 128,128,128

SCREEN_SIZE = (320, 240)

pygame.init()
pygame.camera.init()
pygame.mouse.set_visible(False)

screen = pygame.display.set_mode(SCREEN_SIZE)
class Capture(object):
    def __init__(self):
        self.size = (640,480)
        self.display = pygame.display.set_mode(self.size, 0)
        self.clist = pygame.camera.list_cameras()
        if not self.clist:
            raise ValueError("Sorry, no cameras detected.")
        self.cam = pygame.camera.Camera(self.clist[0], self.size)
        self.cam.start()
        self.snapshot = pygame.surface.Surface(self.size, 0, self.display)

    def get_and_flip(self):
        if self.cam.query_image():
            self.snapshot = self.cam.get_image(self.snapshot)

        self.display.blit(self.snapshot, (0,0))
        pygame.display.flip()

    def main(self):
        going = True
        while going:
            events = pygame.event.get()
            for e in events:
                if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                    # close the camera safely
                    self.cam.stop()
                    going = False

            self.get_and_flip()

setting_labels = [
  {
    'dev': 'cam',
    'text': 'Video',
    'pos': (60, 40),
    'font': pygame.font.Font(None, 30),
    'on': False,
    'online': False,
    'value': '',
    'unit': ''
  },
  {
    'dev': 'mic',
    'text': 'Audio',
    'pos': (160, 40),
    'font': pygame.font.Font(None, 30),
    'on': False,
    'online': False,
    'value': '',
    'unit': ''
  },
  {
    'dev': 'gps',
    'text': 'GPS',
    'pos': (260, 40),
    'font': pygame.font.Font(None, 30),
    'on': False,
    'online': True,
    'value': '',
    'unit': ''
  }, 
  {
    'dev': 'speed',
    'text': '',
    'pos': (100, 105),
    'font': pygame.font.Font(None, 55),
    'on': False,
    'online': True,
    'value': 20,
    'unit': 'km/h'
  },
  {
    'dev': 'acce',
    'text': '',
    'pos': (240, 85),
    'font': pygame.font.Font(None, 35),
    'on': True,
    'online': True,
    'value': 20,
    'unit': 'm/s^2'
  },
 
  {
    'dev': 'rpm',
    'text': '',
    'pos': (240, 120),
    'font': pygame.font.Font(None, 35),
    'on': False,
    'online': False,
    'value': 20,
    'unit': 'RPM'
  },
  {
    'dev': 'coolant',
    'text': 'Coolant: ',
    'pos': (80, 160),
    'font': pygame.font.Font(None, 30),
    'on': True,
    'online': True,
    'value': 20,
    'unit': 'F'
  },
  {
    'dev': 'oil',
    'text': 'Oil: ',
    'pos': (220, 160),
    'font': pygame.font.Font(None, 30),
    'on': False,
    'online': True,
    'value': 20,
    'unit': 'F'
  },
  {
    'dev': 'throttle',
    'text': 'Throttle: ',
    'pos': (80, 200),
    'font': pygame.font.Font(None, 30),
    'on': False,
    'online': True,
    'value': 20,
    'unit': '%'
  },
  {
    'dev': 'brake',
    'text': 'Brake: ',
    'pos': (220, 200),
    'font': pygame.font.Font(None, 30),
    'on': False,
    'online': True,
    'value': 20,
    'unit': 'bar'
  },
]

def button_cb(channel):
  if channel == 17:
    pass
  elif channel == 22:
    pass
  elif channel == 23:
    pass
  elif channel == 27:
    pass


def render_setting_lables(screen, labels):
  for label in labels:
    text = label['text'] + str(label['value']) + label['unit']

    text_color = WHITE
    if not label['online']:
      text_color = GREY
    elif label['on']:
      text_color = GREEN

    label_surface = label['font'].render(text, True, text_color)

    rect = label_surface.get_rect(center=label['pos'])
    screen.blit(label_surface, rect)

def update_screen():
    screen.fill(BLACK)
    render_setting_lables(screen, setting_labels)
    pygame.display.flip()


def main_loop():
  while True:
    for event in pygame.event.get():
      if(event.type is MOUSEBUTTONUP):
        pos = pygame.mouse.get_pos()


# for pin in [17, 22, 23, 27]:
#     GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#     GPIO.add_event_detect(pin, GPIO.FALLING, callback=button_cb, bouncetime=300)

# update_screen()
streaming = Capture()
streaming.main()
main_loop()

_quit()

