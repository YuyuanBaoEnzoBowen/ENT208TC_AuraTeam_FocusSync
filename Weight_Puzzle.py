import os, sys, io
import M5
from M5 import *
from label_plus import LabelPlus
from hardware import Pin
from hardware import I2C
from unit import WeightI2CUnit
from hardware import RGB
import time



label0 = None
label1 = None
label2 = None
i2c0 = None
rgb26 = None
weight_i2c_0 = None


import math

FocusTime = None


def setup():
  global label0, label1, label2, i2c0, rgb26, weight_i2c_0, FocusTime

  M5.begin()
  Widgets.setRotation(0)
  Widgets.fillScreen(0x000000)
  label0 = LabelPlus("label0", 1, 27, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu24, "http://", 3000, True, "title", "error", 0xFF0000)
  label1 = LabelPlus("label1", 27, 102, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu24, "http://", 3000, True, "title", "error", 0xFF0000)
  label2 = LabelPlus("label2", 29, 163, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu24, "http://", 3000, True, "title", "error", 0xFF0000)

  i2c0 = I2C(0, scl=Pin(33), sda=Pin(32), freq=100000)
  weight_i2c_0 = WeightI2CUnit(i2c0, 0x26)
  rgb26 = RGB(io=26, n=3, type="SK6812")
  rgb26.set_brightness(32)
  FocusTime = 30
  rgb26.fill_color(0x000000)


def loop():
  global label0, label1, label2, i2c0, rgb26, weight_i2c_0, FocusTime
  M5.update()
  label0.setText(str((weight_i2c_0.get_weight_str)))
  if (weight_i2c_0.get_weight_int) > 8390000:
    if FocusTime > 0:
      rgb26.set_color(0, 0xcc0000)
      label1.setText(str((str(FocusTime))))
      FocusTime = FocusTime - 1
      label2.setText(str((str((round(FocusTime))))))
    else:
      rgb26.set_color(0, 0xcc0000)
      label1.setText(str('done'))
      label2.setText(str('0'))
  else:
    rgb26.set_color(0, 0xcc0000)
    label1.setText(str('fail'))
    FocusTime = 30
    label2.setText(str('30'))
  time.sleep(1)


if __name__ == '__main__':
  try:
    setup()
    while True:
      loop()
  except (Exception, KeyboardInterrupt) as e:
    try:
      label0.deinit()
      label1.deinit()
      label2.deinit()
      from utility import print_error_msg
      print_error_msg(e)
    except ImportError:
      print("please update to latest firmware")
