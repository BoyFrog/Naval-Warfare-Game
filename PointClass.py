# https://www.pygame.org/docs/tut/tom_games4.html
# https://math.stackexchange.com/questions/163881/calculating-points-in-circles
# https://math.stackexchange.com/questions/227481/x-points-around-a-circle?rq=1
# https://i.stack.imgur.com/ye00R.jpg
# https://tutorialspoint.dev/image/Breshanham.png
# https://www.pygame.org/wiki/2DVectorClass
# https://stackoverflow.com/questions/45420223/pygame-vector2-as-polar-and-vector2-from-polar-methods

import math

def rect(r, theta):
    """theta in degrees
    returns tuple; (float, float); (x,y)
    """
    x = r * math.cos(math.radians(theta))
    y = r * math.sin(math.radians(theta))
    return x, y

def polar(x, y):
    """returns r, theta(degrees)
    """
    r = (x ** 2 + y ** 2) ** .5
    theta = math.degrees(math.atan2(y, x))
    return r, theta

class Point:
    def __init__(self, x=None, y=None, r=None, theta=None):
        if x is not None and y is not None:
            self.c_cartesian(x, y)

        elif r is not None and theta is not None:
            self.c_polar(r, theta)

        else:
            raise ValueError('Must specify x & y or r & theta')

    def c_cartesian(self, x, y):
        self.x = x
        self.y = y
        polarCoord = polar(self.x, self.y)
        self.r = polarCoord[0]
        self.theta = polarCoord[1]
        return

    def c_polar(self, r, theta):
        self.r = r
        self.theta = theta
        cartesianCoord = rect(self.r, self.theta)
        self.x = cartesianCoord[0]
        self.y = cartesianCoord[1]
        return


