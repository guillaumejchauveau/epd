from PIL import Image, ImageFont
import EPDFrame
import utils.graphics.drawing

import time


class TimeFrame(EPDFrame.Frame):
    def __init__(self, display_size, client):
        super(self.__class__, self).__init__(display_size, client)

        date_x0 = 40
        date_y0 = 25
        date_x1 = self.size[0]
        date_y1 = date_y0 + 30

        self._regions['date'] = EPDFrame.FrameRegion((date_x0, date_y0, date_x1, date_y1))
        self._regions['date']['date'] = utils.graphics.drawing.Text()
        self._regions['date']['date'].points.append(date_x0)
        self._regions['date']['date'].points.append(date_y0)
        self._regions['date']['date'].fill = 0
        self._regions['date']['date'].font = ImageFont.truetype('fonts/Roboto-Light.ttf', 30)

        time_font = ImageFont.truetype('fonts/Roboto-Thin.ttf', 100)
        time_y0 = self.size[1] / 2 - 100 / 2 - 10
        time_y1 = time_y0 + 100
        time_width = time_font.getsize('00')[0]
        offset = 15
        hours_x1 = self.size[0] / 2 - offset
        hours_x0 = hours_x1 - time_width
        minutes_x0 = self.size[0] / 2 + offset
        minutes_x1 = minutes_x0 + time_width

        self._regions['hours'] = EPDFrame.FrameRegion((hours_x0, time_y0, hours_x1, time_y1))
        self._regions['hours']['hours'] = utils.graphics.drawing.Text()
        self._regions['hours']['hours'].points.append(hours_x0)
        self._regions['hours']['hours'].points.append(time_y0)
        self._regions['hours']['hours'].fill = 0
        self._regions['hours']['hours'].font = time_font

        self._regions['minutes'] = EPDFrame.FrameRegion((minutes_x0, time_y0, minutes_x1, time_y1))
        self._regions['minutes']['minutes'] = utils.graphics.drawing.Text()
        self._regions['minutes']['minutes'].points.append(minutes_x0)
        self._regions['minutes']['minutes'].points.append(time_y0)
        self._regions['minutes']['minutes'].fill = 0
        self._regions['minutes']['minutes'].font = time_font

    def _load_template(self):
        self._image = Image.open('frames/time/templates/' + str(self.size[0]) + 'x' + str(self.size[1]) + '.bmp')

    def update_regions(self, secs):
        week_day, day, month, hours, minutes = time.strftime('%A:%d:%B:%H:%M', time.localtime(secs)).split(':')

        self._regions['date']['date'].text = week_day + ' ' + day + ' ' + month
        self._regions['hours']['hours'].text = hours
        self._regions['minutes']['minutes'].text = minutes
