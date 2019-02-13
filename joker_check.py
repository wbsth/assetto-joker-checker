##################################
# Joker Check v 0.3.2
# author : Wobo#1287
##################################

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
polygon = []
timer = 0
time_left = 0
session_type = 0
track_supported = 0

def acMain(ac_version):
    global ui_driver_list, track_name, session_type

    appName = "Joker Check"
    appWindow = ac.newApp(appName)
    ac.setSize(appWindow, 150, 150)
    ac.drawBorder(appWindow, 0)
    ac.setIconPosition(appWindow, 0, -10000)

    ui_driver_list = ac.addLabel(appWindow, "Track not supported")
    ac.setPosition(ui_driver_list, 3, 30)

    load_track_name()
    load_polygon()
    load_session_type()

    return appName


def acUpdate(deltaT):
    global ui_driver_list, driver_list, timer, time_left, track_supported

    timer += deltaT

    if track_supported:
        # Limit frequency to 60hz
        if timer > 0.0166:
            timer = 0
            build_driver_list()
            time_left = info.graphics.sessionTimeLeft
            clear_before_race()
            driver_string = '\n'.join(driver_list)
            ac.setText(ui_driver_list, driver_string)
            #ac.console(str(ac.getCarState(0, acsys.CS.WorldPosition))) # logs coordinates to console, helpful at setting joker boundaries

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
            inpitbox = ac.isCarInPit(i)
            isconnected = ac.isConnected(i)
            if not inpitbox and isconnected:
                crds = ac.getCarState(i, acsys.CS.WorldPosition)
                inside_joker = inside_polygon(crds[0], crds[2], polygon)
                if inside_joker:
                    driver_list.append(driver_name)
                    lap = ac.getCarState(i, acsys.CS.LapCount)
                    send_chat_message(driver_name, lap)


def clear_before_race():
    """Clears joker list before race starts"""
    global time_left, driver_list, session_type
    if time_left >= 0:
        driver_list = []


def load_polygon():
    """Try to load joker area coordinates from file"""
    global polygon, track_name, track_supported

    try:
        polygon = []
        path = 'apps/python/joker_check/tracks/{}.txt'.format(track_name)
        with open(path, 'r') as f:
            temp = f.read().splitlines()
            for i in temp:
                tmp_tuple = tuple(map(int, i.split(', ')))
                polygon.append(tmp_tuple)
        track_supported = 1
        ac.log("[JOKER CHECK] Track supported")
    except IOError:
        track_supported = 0
        ac.log("[JOKER CHECK] Track not supported")


def load_track_name():
    """Loads name of track"""
    global track_name
    track_name = ac.getTrackName(0)


def send_chat_message(drv, lap):
    """Sends message to chat to indicate that driver completed joker, also log to py_log"""
    ac.sendChatMessage(" | " + drv + " completed joker on lap " + str(lap + 1))
    ac.log("[JOKER CHECK] " + drv + " completed joker on lap " + str(lap + 1))


def load_session_type():
    """Loads session type"""
    global session_type
    session_type = info.graphics.session
