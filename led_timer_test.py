import os, sys, io
import M5
from M5 import *
from unit import PIRUnit
import time
from hardware import RGB



image0 = None
image1 = None
rgb32 = None
pir_0 = None


i = None


def setup():
  global image0, image1, rgb32, pir_0

  M5.begin()
  Widgets.setRotation(1)
  Widgets.fillScreen(0xffffff)
  image0 = Widgets.Image("/flash/res/img/1.png", 35, -9, scale_x=0.7, scale_y=0.7)
  image1 = Widgets.Image("/flash/res/img/3.png", 38, -6, scale_x=0.3, scale_y=0.3)

  pir_0 = PIRUnit((33, 32))
  rgb32 = RGB(io=32, n=30, type="SK6812")
  Widgets.setRotation(1)
  rgb32.set_brightness(70)
  Widgets.fillScreen(0x000000)
  image0.setVisible(False)
  image1.setVisible(True)
  time.sleep_ms(3000)


def loop():
  global image0, image1, rgb32, pir_0
  if (pir_0.get_status()) == 1:
    image0.setVisible(False)
    Widgets.fillScreen(0xffffff)
    image0.setVisible(True)
    image1.setVisible(False)
    for i in range(1, 21):
      image0.setVisible(True)
      rgb32.fill_color(0xff0000)
      Speaker.tone(4000, 100)
      time.sleep_ms(50)
      rgb32.fill_color(0x3366ff)
      Speaker.tone(3000, 100)
      time.sleep_ms(50)
    rgb32.fill_color(0x000000)
    Speaker.tone(0, 100)
    time.sleep_ms(3000)
  else:
    image1.setVisible(False)
    Widgets.fillScreen(0x000000)
    image0.setVisible(False)
    image1.setVisible(True)
  time.sleep_ms(100)
  M5.update()


if __name__ == '__main__':
  try:
    setup()
    while True:
      loop()
  except (Exception, KeyboardInterrupt) as e:
    try:
      from utility import print_error_msg
      print_error_msg(e)
    except ImportError:
      print("please update to latest firmware")
