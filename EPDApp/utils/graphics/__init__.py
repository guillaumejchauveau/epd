from PIL import Image
import utils


class PixelMatrix(utils.Matrix):
    def __init__(self, image: Image):
        self.__image = image
        self.__matrix = image.load()

        self.__iter_x_cursor = 0
        self.__iter_y_cursor = 0

    def __getitem__(self, position: (int, int)):
        """
        Maps evaluation of self[position] to the matrix.

        :param position: X and Y coordinates.
        :type position: (int, int)
        :return The value at position.
        :rtype int
        """
        return self.__matrix[position]

    def __setitem__(self, position: (int, int), value: int):
        """
        Maps assignment of self[position] to the matrix.

        :param position: X and Y coordinates.
        :type position: (int, int)
        :param value: The value to assign.
        :type value: int
        """
        self.__matrix[position] = value

    def __delitem__(self, position: (int, int)):
        """
        Maps deletion of self[position] to the matrix.

        :param position: X and Y coordinates.
        :type position: (int, int)
        """
        self.__matrix[position] = None

    @property
    def width(self) -> int:
        """
        The width of the matrix.

        :rtype int
        """
        return self.__image.size[0]

    @property
    def height(self) -> int:
        """
        The height of the matrix.

        :rtype int
        """
        return self.__image.size[1]

    @property
    def image(self) -> Image:
        return self.__image

    def slice(self, box: (int, int, int, int)):
        """
        Extracts a piece of the pixel matrix.

        :param box: Defines the rectangle to slice with four lines: left, top, right (excluded) and bottom (excluded).
        :type box: (int, int, int, int)
        :return A new PixelMatrix object.
        :rtype PixelMatrix
        """
        box = list(box)

        for index, axis_value in enumerate(box):
            if axis_value < 0:
                box[index] = 0

            # If odd then it's a vertical axis.
            if index % 2:
                if axis_value > self.height:
                    box[index] = self.height
            else:
                if axis_value > self.width:
                    box[index] = self.width

        return PixelMatrix(self.__image.crop(box))


class Shape:
    def __init__(self, relative_point_positioning=False):
        """
        Creates a Shape object. A shape is a set of Points.
        :param relative_point_positioning: Defines if the points' position is relative to the shape's bounding-box's
        position.
        :type relative_point_positioning: bool
        """
        self.__width = 0
        self.__height = 0
        self.__position_x = None
        self.__position_y = None

        self.__relative_point_positioning = relative_point_positioning
        self.__points = []

    def __getitem__(self, index: int) -> utils.Point:
        """
        Maps evaluation of self[index] to the shape's points.

        :param index: The index of the point.
        :type index: int
        :return The Point.
        :rtype Point
        """
        return self.__points[index]

    def __iter__(self):
        """
        :return An iterator over the shape's points.
        """
        return iter(self.__points)

    def __len__(self):
        """
        :return The number of Points of the shape (its surface).
        """
        return len(self.__points)

    @property
    def width(self) -> int:
        """
        The width of the shape's bounding-box.

        :rtype int
        """
        return self.__width

    @width.setter
    def width(self, value: int):
        """
        width setter.

        :param value: Value for width.
        :type value: int
        """
        if value >= 0:
            self.__width = value

    @property
    def height(self) -> int:
        """
        The height of the shape's bounding-box.

        :rtype int
        """
        return self.__height

    @height.setter
    def height(self, value: int):
        """
        height setter.

        :param value: Value for height.
        :type value: int
        """
        if value >= 0:
            self.__height = value

    @property
    def position_x(self) -> int:
        """
        X position of the top-left corner of the shape's bounding-box.

        :rtype int
        """
        return self.__position_x

    @position_x.setter
    def position_x(self, value: int):
        """
        position_x setter.

        :param value: Value for position_x.
        :type value: int
        """
        if value >= 0:
            self.__position_x = value

    @property
    def position_y(self) -> int:
        """
        Y position of the top-left corner of the shape's bounding-box.

        :rtype int
        """
        return self.__position_y

    @position_y.setter
    def position_y(self, value: int):
        """
        position_y setter.

        :param value: Value for position_y.
        :type value: int
        """
        if value >= 0:
            self.__position_y = value

    @property
    def relative_point_positioning(self) -> bool:
        """
        Defines if the shape's points' position is relative to the shape's bounding-box's position.
        :rtype int
        """
        return self.__relative_point_positioning

    def add_point(self, point: utils.Point):
        """
        Adds a point to the shape and update the shape's bounding-box's position and size accordingly.
        :param point: The Point to add.
        :type point: Point
        """
        h_offset = (0 if self.relative_point_positioning else self.position_x) - point.x
        if h_offset > 0:
            self.position_x = point.x
            self.width += h_offset
        if h_offset <= -self.width:
            self.width = -h_offset + 1

        v_offset = (0 if self.relative_point_positioning else self.position_y) - point.y

        # Theoretically impossible since pixels higher than the start point cannot be part of the shape.
        if v_offset > 0:
            self.position_y = point.y
            self.height += v_offset
        if v_offset <= - self.height:
            self.height = -v_offset + 1

        self.__points.append(point)

    def to_relative_point_positioning(self):
        """
        Creates a new Shape object with all it's points' position relative to the shape's position.
        :return The shape in relative point positioning.
        :rtype Shape
        :raise RuntimeError: RuntimeError is raised if the shape is already in relative point positioning.
        """
        if self.relative_point_positioning:
            raise RuntimeError('Shape already in relative point positioning')

        shape = self.__class__(True)

        shape.position_x = self.position_x
        shape.position_y = self.position_y
        shape.width = self.width
        shape.height = self.height

        for point in self:
            relative_point = utils.Point(point.x - self.position_x, point.y - self.position_y)
            shape.add_point(relative_point)

        return shape

    def to_pil_image(self) -> Image:
        """
        Creates a PIL Image based on the shape's points. It can be used only in relative point positioning.
        :return The PIL Image.
        :rtype: Image
        :raise RuntimeError: RuntimeError is raised if the shape is not in relative point positioning.
        """
        if not self.relative_point_positioning:
            raise RuntimeError('Shape is not in relative point positioning')

        image = Image.new('1', (self.width, self.height), 255)
        image_pixels = image.load()

        for point in self:
            image_pixels[point.x, point.y] = 0

        return image
