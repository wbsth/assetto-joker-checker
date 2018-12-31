####################
# Joker Check v 0.1
# author : Wobo#1287
####################

import sys
import ac
import acsys

ui_driver_list = 0
driver_list = []
track_name = ""
ppl_on_track = 0
polygon = []
timer = 0


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
    global ui_driver_list, driver_list, track_name, ppl_on_track, timer, polygon

    pitlane = ac.isCarInPitLane(0)
    pit = ac.isCarInPit(0)
    ac.console("Pitlane {}".format(str(pitlane)))
    ac.console("Pit {}".format(str(pit)))

    timer += deltaT

    # Limit frequency to 60hz
    if timer > 0.0166:
        timer = 0
        build_driver_list()
        check_on_track()
        clear_if_pits()

        driver_string = '\n'.join(driver_list)
        ac.setText(ui_driver_list, driver_string)


def inside_polygon(x, y, points):
    """
    Return True if a coordinate (x, y) is inside a polygon defined by
    a list of verticies [(x1, y1), (x2, x2), ... , (xN, yN)].

    Reference: http://www.ariel.com.au/a/python-point-int-poly.html
    """
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
                joker_status = inside_polygon(crds[0], crds[2], polygon)
                if joker_status:
                    driver_list.append(driver_name)


def check_on_track():
    """Checks how many cars are outside pits"""
    global ppl_on_track
    count = 0
    car_amount = ac.getCarsCount()
    for i in range(0, car_amount):
        if not ac.isCarInPit(i):
            count += 1
    ppl_on_track = count


def clear_if_pits():
    """Clears joker list if everyone is in pits"""
    global ppl_on_track, driver_list
    if ppl_on_track == 0:
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


def load_track_name():
    """Loads name of track"""
    global track_name
    track_name = ac.getTrackName(0)
    ac.log("Nazwa trasy odczytana")