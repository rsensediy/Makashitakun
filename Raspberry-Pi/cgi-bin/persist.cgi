#!/usr/bin/python
# -*- coding: utf-8 -*-  

'''
 * rSense
 * Copyright (c) 2014 Yukihiro Nomura All rights reserved.
 * rsensesystems@gmail.com
 *
 * rSense is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * rSense is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with rSense.  If not, see <http://www.gnu.org/licenses/>.
 *
 * 2015/01/09
'''

import sqlite3  
import cgi
import cgitb
import time

from xbee import ZigBee
import serial
import struct

import unitlst

PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600
sqlitedb = "/var/db/mydb.db"

# Set your controller's IP addr and this script's path
myurl = '<meta http-equiv=\"refresh\" content=\"0;URL=http://xxx.xxx.xxx.xxx/whatever/rsensectl.psp\">'

cgitb.enable()

print "Content-type: text/html; charset=utf-8"

print '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">

<p><br>
<title>rSense Controll Panel</title>
</head>

'''


unit_id = unitlst.unit1_id

# get saved params from DB
con = sqlite3.connect(sqlitedb)
con.row_factory = sqlite3.Row
cur = con.cursor()
str = "select  MAX(regdate),myid,s1,sense1,actuate1,interval1,mode1,s2,sense2,actuate2,interval2,mode2,s3,sense3,actuate3,interval3,mode3,s4,sense4,actuate4,interval4,mode4,s5,sense5,actuate5,interval5,mode5 from ctltbl where myid=" + "'"+ unit_id +"'"
cur.execute(str)
result = cur.fetchone()

s1 = result[2].encode('utf-8')
sense1 = result[3].encode('utf-8')
actuate1 = result[4].encode('utf-8')
interval1 = result[5].encode('utf-8')
mode1 = result[6].encode('utf-8')

s2 = result[7].encode('utf-8')
sense2 = result[8].encode('utf-8')
actuate2 = result[9].encode('utf-8')
interval2 = result[10].encode('utf-8')
mode2 = result[11].encode('utf-8')

s3 = result[12].encode('utf-8')
sense3 = result[13].encode('utf-8')
actuate3 = result[14].encode('utf-8')
interval3 = result[15].encode('utf-8')
mode3 = result[16].encode('utf-8')

s4 = result[17].encode('utf-8')
sense4 = result[18].encode('utf-8')
actuate4 = result[19].encode('utf-8')
interval4 = result[20].encode('utf-8')
mode4 = result[21].encode('utf-8')

s5 = result[22].encode('utf-8')
sense5 = result[23].encode('utf-8')
actuate5 = result[24].encode('utf-8')
interval5 = result[25].encode('utf-8')
mode5 = result[26].encode('utf-8')

mydata01 = sense1 + s1 + actuate1 + interval1 + mode1 + sense2 + s2 + actuate2 + interval2 + mode2 
mydata02 = sense3 + s3 + actuate3 + interval3 + mode3 + sense4 + s4 + actuate4 + interval4 + mode4 
mydata03 = sense5 + s5 + actuate5 + interval5 + mode5 + sense1 + s1 + actuate1 + interval1 + mode1 

cur.close()

# Send to unit
ser = serial.Serial(PORT, BAUD_RATE)
xbee = ZigBee(ser,escaped=True)
xbee.send('tx',data= mydata01, dest_addr_long= unitlst.unit1_addr, dest_addr='\xff\xfe')
ser.close()

time.sleep(1)

ser = serial.Serial(PORT, BAUD_RATE)
xbee = ZigBee(ser,escaped=True)
xbee.send('tx',data= mydata02, dest_addr_long= unitlst.unit1_addr, dest_addr='\xff\xfe')
ser.close()

time.sleep(1)

ser = serial.Serial(PORT, BAUD_RATE)
xbee = ZigBee(ser,escaped=True)
xbee.send('tx',data= mydata03, dest_addr_long= unitlst.unit1_addr, dest_addr='\xff\xfe')
ser.close()

print "<h2>Activating...</h2>"
print myurl
print "</td></tr></table></center>"
print "</body></html>"
