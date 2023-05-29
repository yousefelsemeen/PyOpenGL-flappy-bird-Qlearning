from random import randint
from itertools import cycle

# ######### Constants ##############
SCREENWIDTH = 600
SCREENHEIGHT = 720
BASEY = SCREENHEIGHT * 0.2
###################################


def random_gap():
    return randint(int(BASEY) + 206, SCREENHEIGHT - 220)


class Pipe:
    def __init__(self):
        self.gap_size = 150
        self.width = 70
        self.gap_y = random_gap()
        self.left = SCREENWIDTH
        self.right = self.left + self.width
        self.upper_y = self.gap_y + self.gap_size * 0.5
        self.lower_y = self.gap_y - self.gap_size * 0.5
        self.count = False  # flag: if the bird has already passed it or not

    def move(self, shift):
        self.left += shift
        self.right += shift


class Bird:
    def __init__(self, gravity=-0.2, angular_s=0.5):
        # shape attributes
        self.height = 40
        self.width = 1.3 * self.height   # width is longer than height
        # position attributes
        self.right = SCREENWIDTH * 0.3
        self.left = self.right - self.width
        self.bottom = SCREENHEIGHT * 0.5
        self.top = self.bottom + self.height
        self.angle = 0
        # movement attributes
        self.fly_speed = 1.1
        self.velocity = 0
        self.gravity = gravity
        self.i_velocity = 0
        self.angular_s = angular_s
        self.i_angular_s = self.angular_s
        # animation Attributes
        self.swap = True


    def fly(self, fly_range=15):
        # moving the bird up or down.
        self.bottom += self.fly_speed
        self.top += self.fly_speed

        # change direction of bird if necessary
        if self.bottom < SCREENHEIGHT * 0.5 - fly_range:
            self.fly_speed *= -1
        if self.bottom > SCREENHEIGHT * 0.5 + fly_range:
            self.fly_speed *= -1

    def move(self):
        if self.bottom > BASEY:
            self.bottom += self.velocity
            self.top += self.velocity
            # control angle variation
            if self.velocity >= 0:  # bird is going up.
                if self.angle < 30:
                    self.angle += self.angular_s
            elif self.angle > -90:  # bird is going down and angle > -90.
                self.angle -= self.angular_s * 0.3

        if self.top >= SCREENHEIGHT:
            self.velocity = 0

        self.velocity += self.gravity

    def die(self):
        self.swap = False
        self.velocity += self.gravity
        self.angular_s += 0.3
        self.move()

    def reset(self):
        # position attributes
        self.right = SCREENWIDTH * 0.3
        self.left = self.right - self.width
        self.bottom = SCREENHEIGHT * 0.5
        self.top = self.bottom + self.height
        self.angle = 0
        # movement attributes
        self.velocity = self.i_velocity
        self.angular_s = self.i_angular_s
        self.swap = True


class Base:
    def __init__(self):
        self.width = 2 * SCREENWIDTH + 5
        self.right = 2 * SCREENWIDTH
        self.left = self.right - self.width
        self.top = BASEY
        self.bottom = 0

    def move(self, dx):
        if self.right <= SCREENWIDTH + 1:
            self.right = 2 * SCREENWIDTH
        self.right += dx
        self.left = self.right - self.width

