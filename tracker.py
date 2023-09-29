from libs import planetTracker as pt
import argparse, time
from skyfield.api import load,Topos
from datetime import datetime,timedelta
from time import strftime, gmtime, localtime
from skyfield import almanac
from tzlocal import get_localzone
import pytz

# Show Menu

parser = argparse.ArgumentParser(
   add_help=False,
   formatter_class=argparse.RawDescriptionHelpFormatter, # This will fix description and epilog format
   epilog="Examples: %(prog)s -listbodies")
parser.add_argument("--body", help="Planet to track from skyfield library", default="")

# Station Location
parser.add_argument("--lat",default=51.4844, help=" Station Latitude.")
parser.add_argument("--lon", default=0.1302, help=" Station Longitude.")
parser.add_argument("--listbodies", action="store_true", default=False, help="List options for --body parameter")

parser.add_argument("--elevation", dest="elevation", default=10, help="Elevation boundary.")
parser.add_argument("--freq",  default=0.0,required=False, help="Help to calculate doppler shift")


# Ephemeris file
planets=load('de421.bsp')
ts=load.timescale()


# Define the parse
args =parser.parse_args()

if args.listbodies:
    bodies=planets.names()
    printNames=[]

    for key in bodies:
        keySet=bodies[key]
        for object in keySet:
            printNames.append(str(object))

    sortPlanets=sorted(printNames)
    for planet in sortPlanets:
        print(planet)
    exit(0) # clean exit without any error

elevation=int(args.elevation)
targetPlanet=args.body
try:
    target=planets[targetPlanet]
except:
    try:
        targetPlanet=targetPlanet + 'barycenter'
        target=planets[targetPlanet]
    except:
        print("Error: Unknown planet: {}".format(targetPlanet))

        exit(1)
earth=planets['earth']
if (args.lat==-999.0 or args.lon==-999.0):
        print("ERROR: Latitude and Longitude are required.")
        exit(1)

topog=Topos(float(args.lat), float(args.lon))
observer= earth + topog

first=True
try:
    while (first):
        first=False
        t=ts.now()   # Auto Time Series (Auto-TS) is an open-source Python library to automate time series analysis and forecasting
        td=datetime.utcnow()

        local=datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        delta=datetime.now()-td
        delta=str(delta).strip(":")[0]
        offset=timedelta(hours=int(delta))

        delta1=10

        aU=observer.at(t).observe(target)

        azimuth, elevation, distance=aU.apparent().altaz()

        azi=azimuth.to('deg').value
        ele=elevation.to('deg').value
        distanceInM=distance.to('m').value # To find velocity
        distanceInKm=distanceInM/1000.0
        distanceInMiles=distanceInKm*0.621371  # Converting km to miles

        futuret=t.utc_datetime()
        futuret=futuret+timedelta(seconds=int(delta))

        futureT=ts.utc(futuret.year, futuret.month, futuret.day, futuret.hour, futuret.minute, futuret.second)
        futureaU=observer.at(futureT).observe(target)
        azimuthf, elevationf, distancef=futureaU.apparent().altaz()

        futureDistance=distancef.to('m').value
        
        relativeVelocity=(futureDistance - distanceInM)/ float(delta)
        iluminate=almanac.fraction_illuminated(planets,targetPlanet,t)  # Return the fraction of the target’s disc that is illuminated.

        


        print("Tracking {}".format(targetPlanet))
        print("Time: {} (UTC+ {})".format(local, offset))

        print("\nAzimuth: {:.2f} degrees".format(azi))
        print("Elevation: {:.2f} degrees".format(ele))

        print("\nDistance in miles: {:.2f} miles\nDistance in kilometers: {:.2f} km".format(distanceInMiles, distanceInKm))
        print("Relative velocity:{:.2f} m/s".format(relativeVelocity))
        print("Percentage Illumination: {:.2f} %".format(iluminate * 100.0))
        
        if args.freq != 0:
            doppler_freq=pt.doppler_shift(float(args.freq),relativeVelocity)
            dopplerShift=doppler_freq- float(args.freq)     # Change in frequency
            print("\nFrequency: {} Hz".format(args.freq))
            print("Doppler Frequency: {:2f} Hz".format(doppler_freq))
            print("Doppler Shift: {:2f} Hz".format(doppler_freq))

        # local zone
        local_zone = get_localzone()
        
        # time in that zone
        local_t = datetime.now(local_zone)
        
        # Rise time Fall time 
        # predicts rise time and fall time of the target
        riseTime=local_t - timedelta(hours=local_t.hour) - timedelta(minutes=local_t.minute) - timedelta(seconds=local_t.second)
        fallTime=riseTime + timedelta(hours=23) +  timedelta(minutes=59) + timedelta(seconds=59)

        # convert to UTC
        utcRise=riseTime.astimezone(pytz.utc) # return a DateTime instance according to the specified time zone parameter tz. 
        utcFall=fallTime.astimezone(pytz.utc) # pytz.utc returns a timezone object for the UTC timezone
        

        rise = ts.utc(utcRise.year, utcRise.month, utcRise.day, utcRise.hour,  utcRise.minute,  utcRise.second)
        fall = ts.utc(utcFall.year, utcFall.month, utcFall.day, utcFall.hour,  utcFall.minute,  utcFall.second)


        # Find the times at which a discrete function of time changes value.
        t, y = almanac.find_discrete(rise, fall,pt.targetDistance(observer,target))  # returns an array

        rise_t = None
        fall_t = None
            
        if len(y) > 0:
            if y[0] == True:
                rise_t = t[0]
                if len(t) > 1:
                    fall_t = t[1]
                else:
                    fall_t = None
            else:
                if len(t) > 1:
                    rise_t = t[1]
                else:
                    rise_t = None
                        
                fall_t = t[0]

        if rise_t is not None:
                print("\nTarget Rise: {} [{}] ".format(rise_t.astimezone(local_zone).strftime('%d/%m/%Y %H:%M:%S'), str(local_zone)))
        else:
                print("\nError: Target Rise time is not found")
                
        if fall_t is not None:
                print("Target Set: {} [{}]".format(fall_t.astimezone(local_zone).strftime('%d/%m/%Y %H:%M:%S'), str(local_zone)))
        else:
                print("\nTarget Set time is not found")


except KeyboardInterrupt:
    pass