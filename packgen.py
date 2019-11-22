#!/usr/bin/env python
#
# convert weather info into a useable WX APRS packet format
#
# does a few built in conversions to conform with american units req'd by the
# APRS spec.
#

import sys, string, time
from socket import *

inputdata = sys.argv[2]

inputtuple = string.split(inputdata)
#print inputtuple

network = 1
name = sys.argv[1]
vers = "W01"
version = "APZW01"
route = "TCPIP"
#mycall = "VK3TST-5"
#passcode = "17833"
host = "echelon.pinegap.net"
port = 10152

authstring = "user %s pass %s vers %s" % (mycall, passcode, vers)
outputdata = "%s>%s,%s:;%-9s*" % (mycall, version, route, name[:9])

# Day & date, zulu time (UT)
try:
	day = string.atoi(inputtuple[2])
	hour = string.atoi(inputtuple[3])

	outputdata = outputdata + "%02d%04dz" % (day, hour)
except ValueError:
	pass

# lat/long, as peroted by the station (limited accuracy)
try:
	latdeg = string.atoi(inputtuple[0][:2])
	latmin = (string.atoi(inputtuple[0][2:]) / 100.0) * 60
	lat = "%d%02.2fS" % (latdeg, latmin)

	longdeg = string.atoi(inputtuple[1][:3])
	longmin = (string.atoi(inputtuple[1][3:]) / 100.0) * 60
	long = "%d%02.2fE" % (longdeg, longmin)

	outputdata = outputdata + "%s/%s_" % (lat, long)
except ValueError:
	pass

# Wind speed and direction must go next
try:
	(winddir, windspd) = string.split(inputtuple[6], '/')
	# convert to mph
	windspd = string.atoi(windspd) * 1.1507771555
	if winddir == "N":
		winddeg = 0.0
	elif winddir == "NNE":
		winddeg = 22.5
	elif winddir == "NE":
		winddeg = 45.0
	elif winddir == "ENE":
		winddeg = 67.5
	elif winddir == "E":
		winddeg = 90.0
	elif winddir == "ESE":
		winddeg = 112.5
	elif winddir == "SE":
		winddeg = 135.0
	elif winddir == "SSE":
		winddeg = 157.5
	elif winddir == "S":
		winddeg = 180.0
	elif winddir == "SSW":
		winddeg = 202.5
	elif winddir == "SW":
		winddeg = 225.0
	elif winddir == "WSW":
		winddeg = 247.5
	elif winddir == "W":
		winddeg = 270.0
	elif winddir == "WNW":
		winddeg = 292.5
	elif winddir == "NW":
		winddeg = 315.0
	elif winddir == "NNW":
		winddeg = 337.5
	else:
		winddeg = 361.0

	outputdata = outputdata + "c%03ds%03dg..." % (winddeg, windspd)
	#outputdata = outputdata + "%03d/%03d" % (winddeg, windspd)

except ValueError:
	#outputdata = outputdata + ".../...g..."
	pass

# Current temperature
try:
	temp = string.atoi(inputtuple[7])

	# I hate fahrenheit
	degf = (temp / (5/9.0)) + 32

	outputdata = outputdata + "t%03d" % (degf)

except ValueError:
	#outputdata = outputdata + "t..."
	pass

#outputdata = outputdata + "r...p...P..."

# Relative humidity
try:
	relhum = string.atoi(inputtuple[8])

	outputdata = outputdata + "h%02d" % (relhum)

except ValueError:
	#outputdata = outputdata + "h.."
	pass

# Barometric preassure
# This can sometimes be the QNH, which for our purposes is the same?
try:
	barpres = string.atof(inputtuple[9][-6:])

	outputdata = outputdata + "b%05d" % (barpres * 10)

except ValueError:
	#outputdata = outputdata + "b....."
	pass

# Type and Source
outputdata = outputdata + "zBoM "

# Extra details not in spec.  Comment needs to be shorter.
# Obligitory copyright for BoM.
if inputtuple[11] != "----":
	outputdata = outputdata + "Curr: %s, " % (inputtuple[11])

(mm, hours) = string.split(inputtuple[10], '/')
#print inputtuple[10], mm, hours, string.atoi(hours)
try:
	mm = string.atof(mm)
	dummy = 1 / mm # Quick and dirty way to jump out if no rainfall
except ValueError:
	pass
except ZeroDivisionError:
	pass
else:
	try:
		if hours == "9>":
			outputdata = outputdata + "Rain: %2.1fmm since 9am, " % (mm)
			#outputdata = outputdata + "R %2.1fmm 9am " % (mm)
		else:
			hours = string.atoi(hours)
			outputdata = outputdata + "Rain: %2.1fmm last %d hours, " % (mm, hours)
	except ValueError:
		pass

outputdata = outputdata + " (c) BoM vk3tst@mabsoft.org"

print authstring
print outputdata

if network == 1:
	# do network stuff:
	s = socket(AF_INET, SOCK_STREAM)
	s.connect((host, port))
	s.send(authstring + "\n")
	s.send(outputdata + "\n")
	time.sleep(2)
	#print s.recv(1024)
	#time.sleep(2)
	#print s.recv(1024)
	s.close()

