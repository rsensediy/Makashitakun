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
import time
from xbee import ZigBee
import serial
import struct
import unitlst

PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600
sqlitedb = "/var/db/mydb.db"

unit_id = unitlst.unit1_id

###########################################
# set your controller's serial number

list = ['\x00\x13\xa2\x00\x40\xA8\x5B\x2E']

###########################################

# Get saved from DB
con = sqlite3.connect(sqlitedb)
con.row_factory = sqlite3.Row
cur = con.cursor()
#str = "select  MAX(regdate),myid,s1,sense1,actuate1,interval1,mode1,s2,sense2,actuate2,interval2,mode2,s3,sense3,actuate3,interval3,mode3,s4,sense4,actuate4,interval4,mode4,s5,sense5,actuate5,interval5,mode5 from ctltbl where myid=" + "'"+ unit_id +"'"

# 1212 means to request sending sensor data,you can change whatever you name it.
s1 = '1212'
sense1 = '1212'
actuate1 = '1212'
interval1 = '1212'
mode1 = '1212'

mydata01 = sense1 + s1 + actuate1 + interval1 + mode1

for i,unitaddr in enumerate(list):
        ser = serial.Serial(PORT, BAUD_RATE)
        xbee = ZigBee(ser,escaped=True)
        xbee.send('tx',data= mydata01, dest_addr_long= unitaddr, dest_addr= '\xff\xfe')

	response = xbee.wait_read_frame()

        if not response:
               time.sleep(0.1)
               contine

        if response.has_key('rf_data'):
               ser.close()
               time.sleep(0.1)

	def hex(bindata):
    		return ''.join('%02x' % ord(byte) for byte in bindata)

	# Open serial port
	ser = serial.Serial(PORT, BAUD_RATE)

	# Create API object
	xbee = ZigBee(ser,escaped=True)

	response = xbee.wait_read_frame()

        if not response:
               time.sleep(0.1)
               contine

        if response.has_key('rf_data'):

		sa = hex(response['source_addr_long'][4:])
		rf = hex(response['rf_data'])
		datalength=len(rf)

		# if datalength is compatible with two floats
		# then unpack the 4 byte chunks into floats
		if datalength==56:
			h=struct.unpack('f',response['rf_data'][0:4])[0]
			t=struct.unpack('f',response['rf_data'][4:8])[0]
			t2=struct.unpack('f',response['rf_data'][8:12])[0]
			t3=struct.unpack('f',response['rf_data'][12:16])[0]
			t4=struct.unpack('f',response['rf_data'][16:20])[0]
			t5=struct.unpack('f',response['rf_data'][20:24])[0]
			t6=struct.unpack('f',response['rf_data'][24:28])[0]
			t4s = round(t4,2)
			t5s = round(t5,2)
			#print sa,' ',rf,' t=',t,'h=',h,'h1=',t2,'h2=',t3,'t2=',t4s,'t3=',t5s,'light=',t6

			con = sqlite3.connect(sqlitedb)
			con.text_factory = str

			try:
            			con.executescript("""create table datatbl(regdate timestamp,myid varchar(10),data1 real, data2 real, data3 real, data4 real, data5 real, data6 real, data7 real);""")
            			con.commit()
        		except:
            			print
        		finally:
            			cur = con.cursor()
            			cur.execute("insert into datatbl values(datetime('now','localtime'),?,?,?,?,?,?,?,?)",(sa,h,t,t2,t3,t4s,t5s,t6))
            			con.commit()
            			cur.close()
            			con.close()
	else:
  		print sa,' ',rf

	ser.close()

