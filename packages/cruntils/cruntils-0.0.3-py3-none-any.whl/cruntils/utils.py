
import math

def Cos2(angle):
    return math.pow(math.cos(angle), 2)

def Cos3(angle):
    return math.pow(math.cos(angle), 3)

def Cos4(angle):
    return math.pow(math.cos(angle), 4)

def Cos5(angle):
    return math.pow(math.cos(angle), 5)

def Tan2(angle):
    return math.pow(math.tan(angle), 2)

def Tan3(angle):
    return math.pow(math.tan(angle), 3)

def Tan4(angle):
    return math.pow(math.tan(angle), 4)

def Tan5(angle):
    return math.pow(math.tan(angle), 5)

def DegToRad(degrees):
    """ Convert degrees to radians.
    """
    return (degrees / 180) * math.pi

def RadToDeg(radians):
    """ Convert radians to degrees.
    """
    return (radians / math.pi) * 180

def Circumference(radius):
    """ Circumference of a circle.
    """
    return 2 * math.pi * radius

def ToSignedAngle(angle, degrees=True):
    """ Convert an angle to the range -180 to 180.
    """

    # Degrees.
    if degrees:
        while angle > 180:
            angle = angle - 360
        while angle < -180:
            angle = angle + 360

    return angle

def ToUnsignedAngle(angle, degrees=True):
    """ Convert an angle to the range 0 to 360.
    """

    # Degrees.
    if degrees:
        while angle > 360:
            angle -= 360
        while angle < 0:
            angle += 360

    return angle

def DdToDms(dd, latitude=True, degrees=True):
    """ Convert decimal degrees angle to degrees minutes seconds string.
    """

    # Work with positive numbers.
    dd_temp = dd
    if dd < 0:
        dd_temp *= -1

    # Calculate components.
    degrees = math.floor(dd_temp)
    minutes = math.floor((dd_temp - degrees) * 60)
    seconds = (dd_temp - degrees - (minutes / 60)) * 3600
    seconds = round(seconds, 3)

    # Stringify degrees.
    if latitude:
        degrees_str = f"{degrees}".rjust(2, "0")
    else:
        degrees_str = f"{degrees}".rjust(3, "0")
    
    # Stringify minutes.
    minutes_str = f"{minutes}".rjust(2, "0")

    # Stringify seconds.
    seconds_str_parts = f"{seconds}".split(".")
    seconds_str = seconds_str_parts[0].rjust(2, "0") + "." + seconds_str_parts[1].ljust(3, "0")

    # Full string.
    dms_str = f"{degrees_str} {minutes_str} {seconds_str} "

    # Correct N/S or E/W.
    if dd > 0:
        if latitude:
            dms_str += "N"
        else:
            dms_str += "E"
    else:
        if latitude:
            dms_str += "S"
        else:
            dms_str += "W"

    return dms_str

def LatLonDdToDms(lat, lon, degrees=True):
    """ Convert a DD lat/lon pair to a DMS string.
    """
    dms_lat = DdToDms(lat, True)
    dms_lon = DdToDms(lon, False)
    return f"{dms_lat},{dms_lon}"