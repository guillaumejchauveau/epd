from PIL import Image, ImageDraw
import EPDClient
import collections


class FrameRegion(collections.UserDict):
    def __init__(self, box: (int, int, int, int), fill=255):
        super(self.__class__, self).__init__()
        self.__box = list(box)
        self.__fill = fill

    @property
    def box(self):
        return self.__box

    @property
    def fill(self):
        return self.__fill

    @fill.setter
    def fill(self, value: int):
        if 0 > value > 255:
            raise ValueError

        self.__fill = value

    def draw(self, draw: ImageDraw):
        draw.rectangle(self.box, self.fill)

        for drawing_name in self:
            self[drawing_name].draw(draw)


class Frame:
    def __init__(self, display_size: (int, int), client: EPDClient):
        self.__frame_path = '/var/epd/frame.bmp'

        self.__client = client

        self.__size = display_size
        self._load_template()
        self._draw = ImageDraw.Draw(self._image)

        self._regions = {}

    @property
    def size(self):
        return self.__size

    def _load_template(self):
        self._image = Image.new('1', self.__size, 255)
        main_region = FrameRegion((0, 0, self.size[0], self.size[1]))
        self._regions['main'] = main_region

    def display(self):
        for region_name in self._regions:
            self._regions[region_name].draw(self._draw)

        self._image.copy().rotate(180).save(self.__frame_path)
        self.__client.update()


