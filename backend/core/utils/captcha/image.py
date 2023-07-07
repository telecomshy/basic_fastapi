# coding: utf-8
"""
    captcha.image
    ~~~~~~~~~~~~~

    Generate Image CAPTCHAs, just the normal image CAPTCHAs you are using.
"""

import os
import random
from PIL import Image
from PIL import ImageFilter
from PIL.ImageDraw import Draw
from PIL.ImageFont import truetype
from io import BytesIO

DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')
DEFAULT_FONTS = [os.path.join(DATA_DIR, 'DroidSansMono.ttf')]

__all__ = ['ImageCaptcha']

table = [int(i * 1.97) for i in range(256)]


class ImageCaptcha:
    def __init__(
            self,
            width=160,
            height=60,
            fonts=None,
            font_sizes=None,
            color=None,
            background=None,
            dot_size=2,
            dot_number=30,
            curve_number=1,
            max_rotate_angle=30
    ):
        self.width = width
        self.height = height
        self.fonts = fonts or DEFAULT_FONTS
        self.font_sizes = font_sizes or (42, 50, 56)
        self.color = color or random_color(60, 180, random.randint(220, 255))
        self.background = background or random_color(225, 255)
        self.dot_size = dot_size
        self.dot_number = dot_number
        self.curve_number = curve_number
        self.max_rotate_angle = max_rotate_angle
        self._truefonts = []

    @property
    def truefonts(self):
        if self._truefonts:
            return self._truefonts
        self._truefonts = tuple([truetype(n, s) for n in self.fonts for s in self.font_sizes])
        return self._truefonts

    def create_noise_curve(self, image):
        draw = Draw(image)
        x1 = random.randint(0, int(self.width / 5))
        x2 = random.randint(self.width - int(self.width / 5), self.width)
        y1 = random.randint(int(self.height / 5), self.height - int(self.height / 5))
        y2 = random.randint(y1, self.height - int(self.height / 5))
        points = [x1, y1, x2, y2]
        end = random.randint(160, 200)
        start = random.randint(0, 20)
        draw.arc(points, start, end, fill=self.color)

    def create_noise_dots(self, image):
        draw = Draw(image)
        x1 = random.randint(0, self.width)
        y1 = random.randint(0, self.height)
        draw.line(((x1, y1), (x1 - 1, y1 - 1)), fill=self.color, width=self.dot_size)

    def draw_character(self, image, c):
        draw = Draw(image)
        font = random.choice(self.truefonts)

        p1, p2, p3, p4 = draw.textbbox((0, 0), c, font=font)
        w, h = p3 - p1, p4 - p2

        dx = random.randint(0, 4)
        dy = random.randint(0, 6)
        im = Image.new('RGBA', (w + 2 * dx, h + 2 * dy))
        Draw(im).text((dx, dy), c, font=font, fill=self.color, anchor='lt')

        # rotate
        im = im.crop(im.getbbox())
        im = im.rotate(random.uniform(-self.max_rotate_angle, self.max_rotate_angle), Image.BILINEAR, expand=True)

        # # warp
        dx = w * random.uniform(0.1, 0.3)
        dy = h * random.uniform(0.2, 0.3)
        x1 = int(random.uniform(-dx, dx))
        y1 = int(random.uniform(-dy, dy))
        x2 = int(random.uniform(-dx, dx))
        y2 = int(random.uniform(-dy, dy))
        w2 = w + abs(x1) + abs(x2)
        h2 = h + abs(y1) + abs(y2)
        data = (
            x1, y1,
            -x1, h2 - y2,
            w2 + x2, h2 + y2,
            w2 - x2, -y1,
        )

        im = im.resize((w2, h2))
        im = im.transform((w2, h2), Image.QUAD, data)
        return im

    def create_captcha_image(self, chars):
        image = Image.new('RGB', (self.width, self.height), self.background)

        images = [self.draw_character(image, c) for c in chars]
        text_width = sum([im.size[0] for im in images])

        width = max(text_width, self.width)
        image = image.resize((width, self.height))

        average = int(text_width / len(chars))
        offset = int(average * 0.1)
        rand = int(0.15 * average)  # 控制字符和字符之间重合

        for im in images:
            w, h = im.size
            mask = im.convert('L').point(table)
            image.paste(im, (offset, int((self.height - h) / 2)), mask)
            offset = offset + w + random.randint(-rand, rand)

        image = image.resize((self.width, self.height))

        for _ in range(self.dot_number):
            self.create_noise_dots(image)

        for _ in range(self.curve_number):
            self.create_noise_curve(image)

        return image.filter(ImageFilter.SMOOTH)

    def generate(self, chars, file_type='png'):
        im = self.create_captcha_image(chars)
        out = BytesIO()
        im.save(out, format=file_type)
        out.seek(0)
        return out

    def write(self, chars, output, file_type='png'):
        im = self.create_captcha_image(chars)
        return im.save(output, format=file_type)


def random_color(start, end, opacity=None):
    red = random.randint(start, end)
    green = random.randint(start, end)
    blue = random.randint(start, end)
    if opacity is None:
        return red, green, blue
    return red, green, blue, opacity
