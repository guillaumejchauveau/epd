from PIL import Image, ImageFont
import EPDFrame
import os
import random


class WallpaperFrame(EPDFrame.Frame):
    def _load_template(self):
        wallpapers = os.listdir('frames/wallpaper/templates/')
        wp_path = 'frames/wallpaper/templates/' + random.choice(wallpapers) + '/' + str(self.size[0]) + 'x' + \
                  str(self.size[1]) + '.bmp'

        self._image = Image.open(wp_path)
