from PIL import ImageDraw, ImageFont


class Drawing:
    def draw(self, draw):
        raise NotImplementedError


class PositionableDrawing:
    def __init__(self, points_count=None):
        self.__points_count = None
        self.__points = None

        self._positionable(points_count)

    def _positionable(self, points_count=None):
        self.__points_count = points_count
        self.__points = []

    @property
    def points(self) -> list:
        return self.__points

    @points.setter
    def points(self, points):
        self.__points = points


class FillableDrawing:
    def __init__(self):
        self.__fill = None

        self._fillable()

    def _fillable(self):
        self.__fill = None

    @property
    def fill(self) -> int:
        return self.__fill

    @fill.setter
    def fill(self, fill):
        self.__fill = fill


class OutlineableDrawing:
    def __init__(self):
        self.__outline = None

        self._outlineable()

    def _outlineable(self):
        self.__outline = None

    @property
    def outline(self) -> int:
        return self.__outline

    @outline.setter
    def outline(self, outline: int):
        self.__outline = outline


class AngleableDrawing:
    def __init__(self):
        self.__start = None
        self.__end = None

        self._angleable()

    def _angleable(self):
        self.__start = None
        self.__end = None

    @property
    def start(self) -> int:
        return self.__start

    @start.setter
    def start(self, value: int):
        self.__start = value

    @property
    def end(self) -> int:
        return self.__end

    @end.setter
    def end(self, value: int):
        self.__end = value


class Bitmap(Drawing, PositionableDrawing, FillableDrawing):
    def __init__(self):
        super().__init__()

        self._positionable(1)
        self._fillable()

        self.__bitmap = None

    @property
    def bitmap(self):
        return self.__bitmap

    @bitmap.setter
    def bitmap(self, value):
        self.__bitmap = value

    def draw(self, draw: ImageDraw):
        draw.bitmap(self.points, self.bitmap, self.fill)


class Points(Drawing, PositionableDrawing, FillableDrawing):
    def __init__(self):
        super().__init__()

        self._positionable()
        self._fillable()

    def draw(self, draw: ImageDraw):
        draw.point(self.points, self.fill)


class Lines(Drawing, PositionableDrawing, FillableDrawing):
    def __init__(self):
        super().__init__()

        self._positionable()
        self._fillable()

        self.__width = 0

    @property
    def width(self):
        return self.__width

    @width.setter
    def width(self, value):
        self.__width = value

    def draw(self, draw: ImageDraw):
        draw.line(self.points, self.fill, self.width)


class Polygon(Drawing, PositionableDrawing, FillableDrawing, OutlineableDrawing):
    def __init__(self):
        super().__init__()

        self._positionable()
        self._fillable()
        self._outlineable()

    def draw(self, draw: ImageDraw):
        draw.polygon(self.points, self.fill, self.outline)


class Rectangle(Polygon):
    def __init__(self):
        super().__init__()

        self._positionable(2)


class Arc(Drawing, PositionableDrawing, AngleableDrawing, FillableDrawing):
    def __init__(self):
        super().__init__()

        self._positionable(2)
        self._angleable()
        self._fillable()

    def draw(self, draw: ImageDraw):
        draw.arc(self.points, self.start, self.end, self.fill)


class PieSlice(Arc, OutlineableDrawing):
    def __init__(self):
        super().__init__()

        self._outlineable()

    def draw(self, draw: ImageDraw):
        draw.pieslice(self.points, self.start, self.end, self.fill, self.outline)


class Chord(Arc, OutlineableDrawing):
    def __init__(self):
        super().__init__()

        self._outlineable()

    def draw(self, draw: ImageDraw):
        draw.chord(self.points, self.start, self.end, self.fill, self.outline)


class Ellipse(Drawing, PositionableDrawing, FillableDrawing, OutlineableDrawing):
    def __init__(self):
        super().__init__()

        self._positionable(2)
        self._fillable()
        self._outlineable()

    def draw(self, draw: ImageDraw):
        draw.ellipse(self.points, self.fill, self.outline)


class Text(Drawing, PositionableDrawing, FillableDrawing):
    def __init__(self):
        super().__init__()

        self._positionable(1)
        self._fillable()

        self.__text = ''
        self.__font = None
        self.__anchor = None
        self.__spacing = 0
        self.__align = 'left'
        self.__direction = None
        self.__features = None

    @property
    def text(self) -> str:
        return self.__text

    @text.setter
    def text(self, value: str):
        self.__text = value

    @property
    def font(self) -> ImageFont:
        return self.__font

    @font.setter
    def font(self, value: ImageFont):
        self.__font = value

    @property
    def anchor(self):
        return self.__anchor

    @anchor.setter
    def anchor(self, value):
        self.__anchor = value

    @property
    def spacing(self) -> int:
        return self.__spacing

    @spacing.setter
    def spacing(self, value: int):
        self.__spacing = value

    @property
    def align(self) -> str:
        return self.__align

    @align.setter
    def align(self, value: str):
        if value not in ['left', 'center', 'right']:
            raise ValueError

        self.__align = value

    @property
    def direction(self) -> str:
        return self.__direction

    @direction.setter
    def direction(self, value: str):
        if value not in ['rtl', 'ltr', 'ttb', 'btt']:
            raise ValueError

        self.__direction = value

    @property
    def features(self) -> str:
        return self.__features

    @features.setter
    def features(self, value: str):
        self.__features = value

    def draw(self, draw: ImageDraw):
        draw.text(self.points, self.text, self.fill, self.font, self.anchor, self.spacing, self.align,
                  self.direction, self.features)
