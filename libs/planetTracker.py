from skyfield.nutationlib import iau2000b
from datetime import datetime

from skyfield.nutationlib import iau2000b


def targetDistance(observer, target):
    station=observer.at
    # Planet at time t
    def planet_at(t):
        t._nutation_angles=iau2000b(t.tt)
        # Altitude Azimuth
        return station(t).observe(target).apparent().altaz()[0].degrees > -0.8333 # Index value=0
    # how much it happens a day
    planet_at.rough_period = 0.5  # twice a day
    return planet_at


def doppler_shift(frequency, relativeVelocity):
    """
    Doppler Shift is the apparent change in frequency of a wave in relation to an observer moving relative to the wave source.
    How fast things are moving away or toward of us
    Frequency will never change for source but there will be shift in frequency for stationary.
    So shift in frequency for observer,
    f0 = f{(v+-v0)/v}, where,
    f0 = observed frequency,
    f =  provided frequecy or source frequency,
    v = speed of light
    
    Simplifying the equation,
    we get,
    f0= f+- f*(v0/v)           [ positive or negative depends on velocity moving away or moving towards ]

    Input:
    frequency           = satellite's frequecy in Hz
    relativeVelocity    = satellite is moving at velocity in m/s

    return shift in frequency due to doppler effect or shift
    """
    return (frequency - frequency * (relativeVelocity/3e8))  # velocity of light in m/s


"""
from https://github.com/skyfielders/python-skyfield.git

def iau2000b(jd_tt):
    Compute Earth nutation based on the faster IAU 2000B nutation model.

    `jd_tt` - Terrestrial Time: Julian date float, or NumPy array of floats

    Returns a tuple ``(delta_psi, delta_epsilon)`` measured in tenths of
    a micro-arcsecond.  Each is either a float, or a NumPy array with
    the same dimensions as the input argument.  The result will not take
    as long to compute as the full IAU 2000A series, but should still
    agree with ``iau2000a()`` to within a milliarcsecond between the
    years 1995 and 2020.

    
    dpsi, deps = iau2000a(jd_tt, 2, 77, 0)
    dpsi += -0.000135e7
    deps +=  0.000388e7
    return dpsi, deps
"""

"""
from https://github.com/skyfielders/python-skyfield.git

class Topos(GeographicPosition):
    #Deprecated: use ``wgs84.latlon()`` or ``iers2010.latlon()`` instead.

    def __init__(self, latitude=None, longitude=None, latitude_degrees=None,
                 longitude_degrees=None, elevation_m=0.0, x=0.0, y=0.0):

        if latitude_degrees is not None:
            pass
        elif isinstance(latitude, Angle):
            latitude_degrees = latitude.degrees
        elif isinstance(latitude, (str, float, tuple)):
            latitude_degrees = _ltude(latitude, 'latitude', 'N', 'S')
        else:
            raise TypeError('please provide either latitude_degrees=<float>'
                            ' or latitude=<skyfield.units.Angle object>'
                            ' with north being positive')

        if longitude_degrees is not None:
            pass
        elif isinstance(longitude, Angle):
            longitude_degrees = longitude.degrees
        elif isinstance(longitude, (str, float, tuple)):
            longitude_degrees = _ltude(longitude, 'longitude', 'E', 'W')
        else:
            raise TypeError('please provide either longitude_degrees=<float>'
                            ' or longitude=<skyfield.units.Angle object>'
                            ' with east being positive')

        # Sneaky: the model thinks it's creating an object when really
        # it's just calling our superclass __init__() for us.  Alas, the
        # crimes committed to avoid duplicating code!  (This is actually
        # quite clean compared to the other alternatives I tried.)
        iers2010.latlon(latitude_degrees, longitude_degrees, elevation_m,
                        super(Topos, self).__init__)

        self.R_lat = self._R_lat  # On this old class, it was public.

    def itrf_xyz(self):
        return self.itrs_xyz
"""
