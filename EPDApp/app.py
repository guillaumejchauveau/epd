#!/usr/bin/python3

import locale
import time
import SevenFiveEPD
import EPDClient
import utils.os

from frames.time import TimeFrame
from frames.wallpaper import WallpaperFrame

locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

terminator = utils.os.Terminator()

client = EPDClient.EPDClient()
client.connect()

# frame = TimeFrame.TimeFrame((SevenFiveEPD.width, SevenFiveEPD.height), client)
frame = WallpaperFrame.WallpaperFrame((SevenFiveEPD.width, SevenFiveEPD.height), client)

time_update_freq = 30
time_update_offset = 12
time_precision = 5
last_time = 0
while not terminator.exit:
    time.sleep(time_precision)
    current_time = time.time()
    print(time.strftime('%M:%S', time.localtime(last_time)), time.strftime('%M:%S', time.localtime(current_time)),
          time.strftime('%M:%S', time.localtime(last_time + 60 - time_update_offset)))

    if current_time > (last_time + time_update_freq - time_update_offset):
        client.init()
        # frame.update_regions(current_time + time_update_offset)
        frame.display()
        client.sleep()

        last_time = current_time - current_time % 60 + time_update_freq

client.disconnect()
