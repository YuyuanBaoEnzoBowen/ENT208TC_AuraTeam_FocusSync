import os, sys, io
import M5
from M5 import *
from label_plus import LabelPlus
from hardware import RGB
from hardware import Pin
from hardware import I2C
from unit import WeightI2CUnit
from unit import EncoderUnit
import time



label0 = None
label1 = None
label2 = None
rgb26 = None
i2c0 = None
weight_i2c_0 = None
encoder_0 = None


import math

FocusTime = None
IsRunning = None


def setup():
  global label0, label1, label2, rgb26, i2c0, weight_i2c_0, encoder_0, FocusTime, IsRunning

  M5.begin()
  Widgets.setRotation(0)
  Widgets.fillScreen(0x000000)
  label0 = LabelPlus("label0", 24, 37, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu24, "http://", 3000, True, "title", "error", 0xFF0000)
  label1 = LabelPlus("label1", 27, 102, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu24, "http://", 3000, True, "title", "error", 0xFF0000)
  label2 = LabelPlus("label2", 29, 163, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu24, "http://", 3000, True, "title", "error", 0xFF0000)

  rgb26 = RGB(io=26, n=3, type="SK6812")
  i2c0 = I2C(0, scl=Pin(33), sda=Pin(32), freq=100000)
  weight_i2c_0 = WeightI2CUnit(i2c0, 0x26)
  encoder_0 = EncoderUnit(i2c0, 0x40)
  rgb26.set_brightness(32)
  IsRunning = 0
  encoder_0.set_rotary_value(30)
  rgb26.fill_color(0x000000)


def loop():
  global label0, label1, label2, rgb26, i2c0, weight_i2c_0, encoder_0, FocusTime, IsRunning
  M5.update()
  label0.setText(str((weight_i2c_0.get_weight_str)))
  if IsRunning == 0:
    FocusTime = encoder_0.get_rotary_value()
    label2.setText(str((str((round(FocusTime))))))
    if (encoder_0.get_button_status()) == 0:
      if (weight_i2c_0.get_weight_int) > 8390000:
        IsRunning = 1
        time.sleep(1)
  else:
    if (weight_i2c_0.get_weight_int) > 8390000:
      if FocusTime > 0:
        rgb26.fill_color(0x33ff33)
        label1.setText(str('keep on'))
        FocusTime = FocusTime - 1
        label2.setText(str((str((round(FocusTime))))))
      else:
        rgb26.fill_color(0x33ffff)
        label1.setText(str('done'))
        label2.setText(str('0'))
        IsRunning = 0
    else:
      rgb26.fill_color(0xff0000)
      label1.setText(str('fail'))
      FocusTime = 30
      label2.setText(str('30'))
      IsRunning = 0
      encoder_0.set_rotary_value(30)
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
