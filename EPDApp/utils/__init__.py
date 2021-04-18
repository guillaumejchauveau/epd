class Point:
    def __init__(self, x: int, y: int):
        """
        Creates a Point object. Just a point in a matrix.

        :param x: X position of the point.
        :param y: Y position of the point.
        :type x: int
        :type y: int
        """
        self.__x = None
        self.__y = None

        self.x = x
        self.y = y

    @property
    def x(self) -> int:
        """
        X position of the point.

        :rtype int
        """
        return self.__x

    @x.setter
    def x(self, value: int):
        """
        x setter.

        :param value: Value for x.
        :type value: int
        """
        if value >= 0:
            self.__x = value

    @property
    def y(self) -> int:
        """
        Y position of the pixel.

        :rtype int
        """
        return self.__y

    @y.setter
    def y(self, value: int):
        """
        y setter.

        :param value: Value for y.
        :type value: int
        """
        if value >= 0:
            self.__y = value

    def __eq__(self, point):
        """
        Compares 2 points' position.

        :param point: The point to compare to the instance.
        :type point: Point
        :return True if positions are identical, False otherwise.
        :rtype bool
        """
        return self.x == point.x and self.y == point.y

    def __str__(self):
        """
        Creates a convenient string representation for print.

        :return A string containing the coordinates of the point.
        :rtype str
        """
        return '(' + str(self.x) + ', ' + str(self.y) + ')'


class Matrix:
    def __init__(self, width: int, height: int, initial_value=None):
        """
        Creates a Matrix object.

        :param width: The width of the matrix.
        :type width: int
        :param height: The height of the matrix.
        :type height: int
        :param initial_value: The value used to fill the matrix.
        """
        self.__width = width
        self.__height = height

        self.__matrix = []

        for x in range(self.width):
            self.__matrix.append([initial_value] * self.height)

        self.__iter_x_cursor = 0
        self.__iter_y_cursor = 0

    def __getitem__(self, position: (int, int)):
        """
        Maps evaluation of self[position] to the matrix.

        :param position: X and Y coordinates.
        :type position: (int, int)
        :return The value at position.
        """
        x, y = position

        return self.__matrix[x][y]

    def __setitem__(self, position: (int, int), value):
        """
        Maps assignment of self[position] to the matrix.

        :param position: X and Y coordinates.
        :type position: (int, int)
        :param value: The value to assign.
        """
        x, y = position

        self.__matrix[x][y] = value

    def __delitem__(self, position: (int, int)):
        """
        Maps deletion of self[position] to the matrix.

        :param position: X and Y coordinates.
        :type position: (int, int)
        """
        x, y = position

        self.__matrix[x][y] = None

    @property
    def width(self) -> int:
        """
        The width of the matrix.

        :rtype int
        """
        return self.__width

    @property
    def height(self) -> int:
        """
        The height of the matrix.

        :rtype int
        """
        return self.__height

    def slice(self, box: (int, int, int, int)):
        """
        Extracts a piece of the matrix.

        :param box: Defines the rectangle to slice with four lines: left, top, right (excluded) and bottom (excluded).
        :type box: (int, int, int, int)
        :return A new Matrix object.
        :rtype Matrix
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

        width = box[2] - box[0]
        height = box[3] - box[1]

        matrix_slice = self.__class__(width, height)

        for y_cursor in range(box[1], box[3]):
            for x_cursor in range(box[0], box[2]):
                matrix_slice[x_cursor, y_cursor] = self[x_cursor, y_cursor]

        return matrix_slice

    def neighbors(self, position: (int, int), connectivity=1, horizontal=True, vertical=True):
        """
        Slice the matrix with a given element's neighbors.

        :param position: X and Y coordinates.
        :type position: (int, int)
        :param connectivity: The number of neighbors around the pixel to slice.
        :type connectivity: int
        :param horizontal: Determines if the horizontal neighbors have to be taken.
        :type horizontal: bool
        :param vertical: Determines if the vertical neighbors have to be taken.
        :type vertical: bool
        :return The matrix of neighbors.
        :rtype Matrix
        """
        box = [
            *position,
            *position
        ]

        if horizontal:
            box[0] -= connectivity
            box[2] += (connectivity + 1)
        else:
            box[2] += 1
        if vertical:
            box[1] -= connectivity
            box[3] += (connectivity + 1)
        else:
            box[3] += 1

        return self.slice(box)

    def __len__(self):
        """
        :return The surface of the matrix.
        """
        return self.width * self.height

    def __iter__(self):
        self.__iter_x_cursor = 0
        self.__iter_y_cursor = 0

        return self

    def __next__(self):
        if self.__iter_x_cursor >= self.width:
            self.__iter_x_cursor = 0
            self.__iter_y_cursor += 1

        if self.__iter_y_cursor >= self.height:
            raise StopIteration

        self.__iter_x_cursor += 1

        return self[self.__iter_x_cursor - 1, self.__iter_y_cursor]
