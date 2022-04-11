from Roomba import Misc


def kinematics(lin_speed, rot_speed):  # in mm/s and deg/sec
    d = 235
    omega = - rot_speed * 0.0174533  # sign inversion to keep sense of rotation equal to create2 package

    left = (2 * lin_speed + d * omega) / 2
    right = left - d * omega

    left = Misc.constrain(left, -500, 500)
    right = Misc.constrain(right, -500, 500)

    v = ((left + right) / 2)
    omega = ((left - right) / d) / 0.0174533
    return left, right, v, omega
