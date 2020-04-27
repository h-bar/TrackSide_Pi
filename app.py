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

pygame.init()
pygame.mouse.set_visible(False)

screen = pygame.display.set_mode((320, 240))
setting_labels = [
  {
    'text': 'Video',
    'pos': (80, 40),
    'font': pygame.font.Font(None, 30),
    'on': False,
  },
  {
    'text': 'Audio',
    'pos': (80, 80),
    'font': pygame.font.Font(None, 30),
    'on': False
  },
  {
    'text': 'GPS',
    'pos': (80, 120),
    'font': pygame.font.Font(None, 30),
    'on': False
  },
  {
    'text': 'Acce',
    'pos': (80, 160),
    'font': pygame.font.Font(None, 30),
    'on': False
  },
  {
    'text': 'RPM',
    'pos': (80, 200),
    'font': pygame.font.Font(None, 30),
    'on': False
  },
  {
    'text': 'Speed',
    'pos': (220, 40),
    'font': pygame.font.Font(None, 30),
    'on': False
  },
  {
    'text': 'Coolant',
    'pos': (220, 80),
    'font': pygame.font.Font(None, 30),
    'on': False
  },
  {
    'text': 'Oil',
    'pos': (220, 120),
    'font': pygame.font.Font(None, 30),
    'on': False
  },
  {
    'text': 'Throttle',
    'pos': (220, 160),
    'font': pygame.font.Font(None, 30),
    'on': False
  },
  {
    'text': 'Brake',
    'pos': (220, 200),
    'font': pygame.font.Font(None, 30),
    'on': False
  },
]

value_labels = [
  {
    'text': 'Acce: ',
    'pos': (60, 40),
    'font': pygame.font.Font(None, 30),
    'value': 20,
  },
  {
    'text': 'RPM: ',
    'pos': (60, 80),
    'font': pygame.font.Font(None, 30),
    'value': 20,
  },
  {
    'text': 'Speed: ',
    'pos': (60, 120),
    'font': pygame.font.Font(None, 30),
    'value': 20,
  },
  {
    'text': 'Coolant: ',
    'pos': (60, 160),
    'font': pygame.font.Font(None, 30),
    'value': 20,
  },
  {
    'text': 'Oil: ',
    'pos': (200, 40),
    'font': pygame.font.Font(None, 30),
    'value': 20,
  },
  {
    'text': 'Throttle: ',
    'pos': (200, 80),
    'font': pygame.font.Font(None, 30),
    'value': 20,
  },
  {
    'text': 'Brake: ',
    'pos': (200, 120),
    'font': pygame.font.Font(None, 30),
    'value': 20,
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
    label_surface = label['font'].render(label['text'], True, GREEN if label['on'] else RED)
    rect = label_surface.get_rect(center=label['pos'])
    screen.blit(label_surface, rect)

def render_value_lables(screen, labels):
  for label in labels:
    label_surface = label['font'].render(label['text'] + str(label['value']), True, WHITE)
    rect = label_surface.get_rect(center=label['pos'])
    screen.blit(label_surface, rect)


def update_screen():
    screen.fill(BLACK)
    # render_setting_lables(screen, setting_labels)
    render_value_lables(screen, value_labels)
    pygame.display.flip()


def main_loop():
  while True:
    for event in pygame.event.get():
      if(event.type is MOUSEBUTTONUP):
        pos = pygame.mouse.get_pos()


# for pin in [17, 22, 23, 27]:
#     GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#     GPIO.add_event_detect(pin, GPIO.FALLING, callback=button_cb, bouncetime=300)

update_screen()
main_loop()

_quit()

