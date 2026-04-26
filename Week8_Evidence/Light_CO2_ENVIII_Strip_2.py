import os, sys, io
import M5
from M5 import *
from label_plus import LabelPlus
from hardware import RGB
from hardware import Pin
from hardware import I2C
from unit import ENVUnit
from unit import TVOCUnit
from unit import PBHUBUnit
import time



label0 = None
label1 = None
label2 = None
label3 = None
rgb26 = None
i2c0 = None
env3_0 = None
pbhub_0 = None
tvoc_0 = None


i = None


def setup():
  global label0, label1, label2, label3, rgb26, i2c0, env3_0, pbhub_0, tvoc_0

  M5.begin()
  Widgets.setRotation(0)
  Widgets.fillScreen(0x000000)
  label0 = LabelPlus("label0", 24, 21, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu24, "http://", 3000, True, "title", "error", 0xffffff)
  label1 = LabelPlus("label1", 26, 63, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu24, "http://", 3000, True, "title", "error", 0xffffff)
  label2 = LabelPlus("label2", 3, 161, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18, "http://", 3000, True, "title", "error", 0xFF0000)
  label3 = Widgets.Label("label3", 26, 99, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu24)

  rgb26 = RGB(io=26, n=30, type="SK6812")
  i2c0 = I2C(0, scl=Pin(33), sda=Pin(32), freq=100000)
  tvoc_0 = TVOCUnit(i2c0)
  env3_0 = ENVUnit(i2c=i2c0, type=3)
  tvoc_0 = TVOCUnit(i2c0)
  pbhub_0 = PBHUBUnit(i2c0, 0x61)
  rgb26.set_brightness(70)
  label0.setText(str('Label0'))
  label1.setText(str('Label2'))
  label2.setText(str('Label2'))
  label3.setText(str('Label3'))
  Speaker.stop()
  time.sleep_ms(100)


def loop():
  global label0, label1, label2, label3, rgb26, i2c0, env3_0, pbhub_0, tvoc_0
  label0.setText(str((str((env3_0.read_temperature())))))
  label1.setText(str((str((tvoc_0.tvoc())))))
  label3.setText(str(str((pbhub_0.analog_read(0)))))
  if (env3_0.read_temperature()) > 28:
    for i in range(1, 21):
      Speaker.tone(4000, 100)
      time.sleep_ms(50)
      Speaker.tone(3000, 100)
      time.sleep_ms(50)
      label2.setText(str('TEMP ALARM!'))
    Speaker.tone(0, 100)
    label2.setText(str('TEMP ALARM!'))
    time.sleep_ms(5000)
  else:
    Speaker.stop()
  if (pbhub_0.analog_read(0)) > 1000:
    for i in range(1, 21):
      label2.setText(str('TO DARK!'))
      pbhub_0.digital_write(1, 0, 1)
      time.sleep_ms(50)
      pbhub_0.digital_write(1, 0, 0)
      time.sleep_ms(50)
  else:
    pbhub_0.digital_write(1, 0, 0)
  if (tvoc_0.tvoc()) > 250:
    for i in range(1, 21):
      rgb26.fill_color(0xff0000)
      time.sleep_ms(50)
      rgb26.fill_color(0x3366ff)
      time.sleep_ms(50)
      label2.setText(str('OPEN WINDOW'))
    rgb26.fill_color(0x000000)
    label2.setText(str('OPEN WINDOW'))
    time.sleep_ms(100)
  else:
    rgb26.fill_color(0x000000)
  time.sleep_ms(100)
  M5.update()


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
