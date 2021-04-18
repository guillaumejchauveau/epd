from PIL import Image, ImageDraw
import EPDClient
import EPDExceptions


class EPDFrame:
    def __init__(self, display_size: (int, int), client: EPDClient):
        self.__frame_path = '/var/epd/frame.bmp'

        self.__client = client

        self.__load_template()

    def __load_template(self):
        self.__image = Image.new('1', display_size, 255)
        self.__draw = ImageDraw.Draw(self.__image)

    def display(self):
        self.__image.save(self.__frame_path)
        self.__client.update()
