import os, sys, io
import M5
from M5 import *
from label_plus import LabelPlus
from hardware import RGB
from hardware import Pin
from hardware import I2C
from unit import WeightI2CUnit
from unit import EncoderUnit
from unit import ToF90Unit
import time



label0 = None
label1 = None
label2 = None
label3 = None
image0 = None
line0 = None
label_plus0 = None
line1 = None
label_plus1 = None
label_plus2 = None
rgb26 = None
i2c0 = None
weight_i2c_0 = None
encoder_0 = None
minitof90_0 = None


import math

IsRunning = None
FocusTime = None


def setup():
  global label0, label1, label2, label3, image0, line0, label_plus0, line1, label_plus1, label_plus2, rgb26, i2c0, weight_i2c_0, encoder_0, minitof90_0, IsRunning, FocusTime

  M5.begin()
  Widgets.setRotation(0)
  Widgets.fillScreen(0x000000)
  label0 = LabelPlus("label0", 75, 61, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18, "http://", 3000, True, "title", "error", 0xffffff)
  label1 = LabelPlus("label1", 3, 195, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu24, "http://", 3000, True, "title", "error", 0xe700ff)
  label2 = LabelPlus("label2", 34, 163, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu24, "http://", 3000, True, "title", "error", 0xff00d7)
  label3 = Widgets.Label("label3", 85, 96, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  image0 = Widgets.Image("/flash/res/img/Zen.png", 14, 8, scale_x=1, scale_y=1)
  line0 = Widgets.Line(-5, 41, 145, 41, 0xffffff)
  label_plus0 = LabelPlus("Weight:", -2, 61, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18, "http://", 3000, True, "title", "error", 0xf3f3f3)
  line1 = Widgets.Line(0, 128, 140, 128, 0xffffff)
  label_plus1 = LabelPlus("Time & Status", -2, 137, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18, "http://", 3000, True, "title", "error", 0xe1e1e1)
  label_plus2 = LabelPlus("Distance:", -3, 96, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18, "http://", 3000, True, "title", "error", 0xffffff)

  rgb26 = RGB(io=26, n=64, type="SK6812")
  i2c0 = I2C(0, scl=Pin(33), sda=Pin(32), freq=100000)
  encoder_0 = EncoderUnit(i2c0, 0x40)
  weight_i2c_0 = WeightI2CUnit(i2c0, 0x26)
  minitof90_0 = ToF90Unit(i2c0)
  rgb26.set_brightness(32)
  IsRunning = 0
  encoder_0.set_rotary_value(30)
  rgb26.fill_color(0xff0000)


def loop():
  global label0, label1, label2, label3, image0, line0, label_plus0, line1, label_plus1, label_plus2, rgb26, i2c0, weight_i2c_0, encoder_0, minitof90_0, IsRunning, FocusTime
  M5.update()
  label0.setText(str((weight_i2c_0.get_weight_str)))
  label3.setText(str(str((round(minitof90_0.get_range())))))
  label_plus0.setText(str('Weight'))
  label_plus2.setText(str('Distance'))
  label_plus1.setText(str('Time & Status'))
  if (minitof90_0.get_range()) != -1:
    rgb26.fill_color(0xff0000)
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
  else:
    rgb26.fill_color(0xcc33cc)
    label1.setText(str('AWAY!'))


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
      label_plus0.deinit()
      label_plus1.deinit()
      label_plus2.deinit()
      from utility import print_error_msg
      print_error_msg(e)
    except ImportError:
      print("please update to latest firmware")
