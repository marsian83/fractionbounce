# -*- coding: utf-8 -*-
# Copyright (c) 2011-14, Walter Bender
# Copyright (c) 2011, Paulina Clares, Chris Rowe

# Ported to GTK3 - 2012:
# Ignacio Rodríguez <ignaciorodriguez@sugarlabs.org>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with this library; if not, write to the Free Software
# Foundation, 51 Franklin Street, Suite 500 Boston, MA 02110-1335 USA

from math import pi

from gi.repository import GdkPixbuf

from sprites import Sprite
from svg_utils import (svg_header, svg_footer, svg_str_to_pixbuf, svg_rect,
                       extract_svg_payload, svg_from_file, svg_sector,
                       generate_ball_svg)

import logging
_logger = logging.getLogger('fractionbounce-activity')

from sugar3 import profile
COLORS = profile.get_color().to_string().split(',')

SIZE = [85, 120]
BOX = [85, 32]

ANIMATION = {10: (0, 1), 15: (1, 2), 20: (2, 1), 25: (1, 2), 30: (2, 1),
             35: (1, 2), 40: (2, 3), 45: (3, 4), 50: (4, 3), 55: (3, 4),
             60: (4, 3), 65: (3, 4), 70: (4, 5), 75: (5, 6), 80: (6, 5),
             85: (5, 6), 90: (6, 7)}

# Easter Egg animation graphics
TRANSFORMS = ['<g>',
              '<g transform="matrix(0.83251323,0.17764297,-0.48065174, \
1.0074555,27.969568,-8.7531294)">',
              '<g transform="matrix(-0.83251323,0.17764297,0.48065174, \
1.0074555,57.030432,-8.7531294)">',
              '<g transform="matrix(0.57147881,-0.357582,-0.32994345, \
0.96842187,32.525583,15.686767)">',
              '<g transform="matrix(-0.57147881,-0.357582,0.32994345, \
0.96842187,52.474417,15.686767)">',
              '<g transform="matrix(0.39557109,-0.57943591,-0.22838308, \
0.86196565,35.595823,29.733447)">',
              '<g transform="matrix(-0.39557109,-0.57943591,0.22838308, \
0.86196565,49.404177,29.733447)">',
              '<g transform="matrix(1,0,0,0.08410415,0,73.873449)">']

PUNCTURE = \
    '  <g \
     transform="translate(2.5316175, -8)">\
    <path \
       d="m 33.19688,68.961518 c 3.900378,7.602149 10.970659,7.634416 \
13.708164,7.432138"\
       style="fill:none;stroke:#000000;stroke-width:2;stroke-linecap:round;\
stroke-miterlimit:4" />\
    <path \
       d="m 33.031721,77.05429 c 8.199837,0.123635 12.819227,-7.570626 \
12.882372,-8.423089" \
       style="fill:none;stroke:#000000;stroke-width:2;stroke-linecap:round;\
stroke-miterlimit:4" />\
  </g>'

AIR = \
    '  <g \
     transform="matrix(0.63786322,0,0,0.64837179,17.379518,68.534252)"> \
    <path \
       d="M 39.054054,1.75 C 37.741313,16.51834 25.926641,23.082047 \
25.926641,23.082047 l 0,0" \
       style="fill:none;stroke:#0ac9fb;stroke-width:6.0;stroke-linecap:round;\
stroke-miterlimit:4;" />\
    <path \
       d="m 39.710425,1.75 c 1.312741,14.76834 13.127413,21.332047 \
13.127413,21.332047 l 0,0" \
       style="fill:none;stroke:#0ac9fb;stroke-width:6.0;stroke-linecap:round;\
stroke-miterlimit:4" />\
    <path \
       d="m 39.054054,1.75 c 1.969112,3.281854 -0.656371,20.347491 \
-0.656371,20.347491 l 0,0" \
       style="fill:none;stroke:#0ac9fb;stroke-width:6.0;stroke-linecap:round;\
stroke-miterlimit:4" />\
  </g>'


class Ball():
    ''' The Bounce class is used to define the ball and the user
    interaction. '''

    def __init__(self, sprites, filename):
        self._current_frame = 0
        self._frames = []  # Easter Egg animation
        self._sprites = sprites
        self.ball = Sprite(self._sprites, 0, 0, svg_str_to_pixbuf(
            svg_from_file(filename)))

        self.ball.set_layer(3)
        self.ball.set_label_attributes(24, vert_align='top')

        ball = extract_svg_payload(open(filename, 'r'))
        for i in range(8):
            self._frames.append(Sprite(
                self._sprites, 0, 0, svg_str_to_pixbuf(
                    svg_header(SIZE[0], SIZE[1], 1.0) + TRANSFORMS[i] +
                    ball + PUNCTURE + AIR + '</g>' + svg_footer())))

        for frame in self._frames:
            frame.set_layer(3)
            frame.move((0, -SIZE[1]))  # move animation frames off screen

    def new_ball(self, filename):
        ''' Create a ball object and Easter Egg animation from an SVG file. '''
        self.ball.set_shape(svg_str_to_pixbuf(svg_from_file(filename)))
        ball = extract_svg_payload(open(filename, 'r'))
        for i in range(8):
            self._frames[i].set_shape(svg_str_to_pixbuf(
                svg_header(SIZE[0], SIZE[1], 1.0) + TRANSFORMS[i] +
                ball + PUNCTURE + AIR + '</g>' + svg_footer()))

    def new_ball_from_image(self, filename, save_path):
        ''' Just create a ball object from an image file '''
        if filename == '':
            _logger.debug('Image file not found.')
            return
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
            if pixbuf.get_width() > pixbuf.get_height():
                size = pixbuf.get_height()
                x = int((pixbuf.get_width() - size) // 2)
            else:
                size = pixbuf.get_width()
                x = int((pixbuf.get_height() - size) // 2)
            crop = GdkPixbuf.Pixbuf.new(0, True, 8, size, size)
            pixbuf.copy_area(x, 0, size, size, crop, 0, 0)
            scale = crop.scale_simple(85, 85, GdkPixbuf.InterpType.BILINEAR)
            scale.savev(save_path, 'png', [], [])
            self.ball.set_shape(
                svg_str_to_pixbuf(generate_ball_svg(save_path)))
        except Exception as e:
            _logger.error('Could not load image from %s: %s' % (filename, e))

    def new_ball_from_fraction(self, fraction):
        ''' Create a ball with a section of size fraction. '''
        r = SIZE[0] / 2.0
        self.ball.set_shape(svg_str_to_pixbuf(
            svg_header(SIZE[0], SIZE[1], 1.0) +
            svg_sector(r, r + BOX[1], r - 1, 1.999 * pi,
                       COLORS[0], COLORS[1]) +
            svg_sector(r, r + BOX[1], r - 1, fraction * 2 * pi,
                       COLORS[1], COLORS[0]) +
            svg_rect(BOX[0], BOX[1], 4, 4, 0, 0, '#FFFFFF', 'none') +
            svg_footer()))

    def ball_x(self):
        return self.ball.get_xy()[0]

    def ball_y(self):
        return self.ball.get_xy()[1]

    def frame_x(self, i):
        return self._frames[i].get_xy()[0]

    def frame_y(self, i):
        return self._frames[i].get_xy()[1]

    def width(self):
        return self.ball.rect[2]

    def height(self):
        return self.ball.rect[3]

    def move_ball(self, pos):
        self.ball.move(pos)

    def move_ball_relative(self, pos):
        self.ball.move_relative(pos)

    def move_frame(self, i, pos):
        self._frames[i].move(pos)

    def move_frame_relative(self, i, pos):
        self._frames[i].move_relative(pos)

    def hide_frames(self):
        for frame in self._frames:
            frame.move((0, -SIZE[1]))  # hide the animation frames

    def next_frame(self, frame_counter):
        if frame_counter in ANIMATION:
            self._switch_frames(ANIMATION[frame_counter])
        return self._current_frame

    def _switch_frames(self, frames):
        ''' Switch between frames in the animation '''
        self.move_frame(frames[1], (self.frame_x(frames[0]),
                                    self.frame_y(frames[0])))
        self.move_frame(frames[0], ((0, -SIZE[1])))  # hide the frame
        self._current_frame = frames[1]
