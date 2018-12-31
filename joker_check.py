####################
# Joker Check v 0.2
# author : Wobo#1287
####################

import ac, acsys
import platform, os, sys

if platform.architecture()[0] == "64bit":
    sysdir = os.path.dirname(__file__)+'/lib/stdlib'
else:
    sysdir = os.path.dirname(__file__)+'/lib/stdlib64'

sys.path.insert(0, sysdir)
os.environ['PATH'] = os.environ['PATH'] + ";."

from lib.sim_info import info

import ctypes
from ctypes import wintypes

ui_driver_list = 0
driver_list = []
track_name = ""
ppl_on_track = 0
polygon = []
timer = 0
time_left = 0


def acMain(ac_version):
    global ui_driver_list, track_name

    appName = "Joker Check"
    appWindow = ac.newApp(appName)
    ac.setSize(appWindow, 200, 200)

    ui_driver_list = ac.addLabel(appWindow, "Driver list:")
    ac.setPosition(ui_driver_list, 3, 30)

    load_track_name()
    load_polygon()

    return appName


def acUpdate(deltaT):
    global ui_driver_list, driver_list, track_name, ppl_on_track, timer, polygon, time_left

    timer += deltaT

    # Limit frequency to 60hz
    if timer > 0.0166:
        timer = 0
        build_driver_list()
        # check_on_track()
        time_left = info.graphics.sessionTimeLeft
        clear_before_race()
        driver_string = '\n'.join(driver_list)
        ac.setText(ui_driver_list, driver_string)


def inside_polygon(x, y, points):
    """
    Return True if a coordinate (x, y) is inside a polygon defined by
    a list of verticies [(x1, y1), (x2, x2), ... , (xN, yN)].

    Reference: http://www.ariel.com.au/a/python-point-int-poly.html
    """
    if len(points) == 0:
        return False
    else:
        n = len(points)
        inside = False
        p1x, p1y = points[0]
        for i in range(1, n + 1):
            p2x, p2y = points[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside


def build_driver_list():
    """Builds list of cars that drove through joker"""
    global driver_list, polygon

    # Get number of cars
    car_amount = ac.getCarsCount()

    # Iterate through cars
    for i in range(0, car_amount):
        driver_name = ac.getDriverName(i)
        if driver_name not in driver_list:
            inPitbox = ac.isCarInPit(i)
            isConnected = ac.isConnected(i)
            if not inPitbox and isConnected:
                crds = ac.getCarState(i, acsys.CS.WorldPosition)
                inside_joker = inside_polygon(crds[0], crds[2], polygon)
                if inside_joker:
                    driver_list.append(driver_name)


def clear_before_race():
    """Clears joker list before race starts"""
    global time_left, driver_list
    if time_left >= 0:
        driver_list = []


def load_polygon():
    """Loads check-area according to track"""
    global polygon, track_name

    polygon_kouvola = [(2, 65), (-38, 36), (-50, 51), (-18, 72)]
    polygon_holjes = [(-138, -172), (-161, -174), (-158, -146), (-137, -145)]

    # Get proper joker area to check
    if track_name == "kouvolarx":
        polygon = polygon_kouvola
        ac.log("Wczytano polygon Kouvola")
    elif track_name == "holjesrx":
        polygon = polygon_holjes
        ac.log("Wczytano polygon Holjes")
    else:
        polygon = []

def load_track_name():
    """Loads name of track"""
    global track_name
    track_name = ac.getTrackName(0)