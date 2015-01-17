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

import cgi  
import cgitb  
import sqlite3  
import os

from xbee import ZigBee
import serial
import struct

import unitlst
import actulst

PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600
sqlitedb = "/var/db/mydb.db"

# Set your controller's IP addr and this script's path
myurl = '<meta http-equiv=\"refresh\" content=\"0;URL=http://xxx.xxx.xxx.xxx/whatever/rsensectl.psp\">'

# Set your actuator's name and port number here
#actudict = {"スプリンクラー":0002, "ヒーター":0004,"巻き上げ機":0005, "CO2排出器":0006}
actudict = {"潅水チューブ":0004, "ヒーター2":0002,"巻き上げ機":0005, "ヒーター":0006, "設定しない":0000}
  
cgitb.enable()  

print "Content-type: text/html; charset=utf-8"  

print '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"> 

<p><br>
<title>rSense Controll Panel</title> 
</head> 

'''  
  
message = '''
<dt><hr /> 設定値：%(wsense)s ユニット名：%(name)s 送信日時：%(regdate)s</dt><br><br> 
<dd>%(comment)s</dd><br> 
'''  
def hex(bindata):
    return ''.join('%02x' % ord(byte) for byte in bindata)

con = sqlite3.connect(sqlitedb)  
con.text_factory = str 

try:  
	con.executescript("""create table ctltbl(regdate timestamp,myid varchar(10),s1 varchar(4),sense1 varchar(4),actuate1 varchar(4),interval1 varchar(4),mode1 varchar(4), s2 varchar(4),sense2 varchar(4),actuate2 varchar(4),interval2 varchar(4), mode2 varchar(4), s3 varchar(4),sense3 varchar(4),actuate3 varchar(4),interval3 varchar(4), mode3 varchar(4), s4 varchar(4),sense4 varchar(4),actuate4 varchar(4),interval4 varchar(4),  mode4 varchar(4), s5 varchar(4),sense5 varchar(4),actuate5 varchar(4),interval5 varchar(4), mode5 varchar(4));""")

 	unit_id = unitlst.unit1_id
        cur = con.cursor()
	cur.execute("insert into ctltbl values(datetime('now','localtime'),?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(unit_id,'8888','0000','0000','0000','0000','8888','0000','0000','0000','0000','8888','0000','0000','0000','0000','8888','0000','0000','0000','0000','8888','0000','0000','0000','0000'))
	con.commit()
except:  
	print  
finally:  

	form = cgi.FieldStorage() 
	if form.has_key('sensorid'): 

		# Which sensor
		command =  form.getfirst('sensorid','') 

		# and which actuator to be binded
		moistactuname =  form.getfirst('wmoistactu','') 
		temp1actuname =  form.getfirst('temp1actu','') 
		temp2actuname =  form.getfirst('temp2actu','') 
		humedactuname =  form.getfirst('humedactu','') 
		lightactuname =  form.getfirst('lightactu','') 

  		#if command == 'wmoist'  and moistactuname != 'na': 
  		if command == 'wmoist': 

		        if moistactuname == '潅水チューブ':
                        	actuport = str(actudict["潅水チューブ"])	
				actuportpost = '000' + actuport
			elif moistactuname == 'ヒーター':
                        	actuport = str(actudict["ヒーター"])	
				actuportpost = '000' + actuport
			elif moistactuname == '巻き上げ機':
                        	actuport = str(actudict["巻き上げ機"])	
				actuportpost = '000' + actuport
			elif moistactuname == '設定しない':
                        	actuport = str(actudict["設定しない"])	
				actuportpost = '000' + actuport

			unit_id = unitlst.unit1_id
			
			con.row_factory = sqlite3.Row
			cur = con.cursor()
			str = "select  MAX(regdate),myid,s1,sense1,actuate1,interval1,mode1,s2,sense2,actuate2,interval2,mode2,s3,sense3,actuate3,interval3,mode3,s4,sense4,actuate4,interval4,mode4,s5,sense5,actuate5,interval5,mode5 from ctltbl where myid=" + "'"+ unit_id +"'"
			cur.execute(str)
			result = cur.fetchone()
			
			slide1 = form.getfirst('slide','').encode('utf-8') 
			slide1pint = form.getfirst('slide','')
			slide1int = int(slide1pint)
			if slide1int >= 1000 :
				slide1a = slide1
			elif slide1int < 1000 and slide1int >= 100 :
				slide1a = '0' + slide1 
			elif slide1int < 100 and slide1int >= 10 :
				slide1a = '00' + slide1 
			else:
				slide1a = '000' + slide1

			myid = unitlst.unit1_id
			
			s1 = '7777'
			sense1 = '1111'
			actuate1 = actuportpost 
			interval1 = slide1a
			mode1 = form.getfirst('wmoistmode','').encode('utf-8')

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

			cur = con.cursor() 
			cur.execute("insert into ctltbl values(datetime('now','localtime'),?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(cgi.escape(myid),cgi.escape(s1), cgi.escape(sense1), cgi.escape(actuate1), cgi.escape(interval1),cgi.escape(mode1), cgi.escape(s2), cgi.escape(sense2), cgi.escape(actuate2), cgi.escape(interval2),cgi.escape(mode2), cgi.escape(s3), cgi.escape(sense3), cgi.escape(actuate3), cgi.escape(interval3),cgi.escape(mode3), cgi.escape(s4), cgi.escape(sense4), cgi.escape(actuate4), cgi.escape(interval4),cgi.escape(mode4), cgi.escape(s5), cgi.escape(sense5), cgi.escape(actuate5), cgi.escape(interval5),cgi.escape(mode5)))  
			con.commit()  

  		elif command == 'temp1' and temp1actuname != 'na' :	

                        if temp1actuname == '潅水チューブ':
                                actuport = str(actudict["潅水チューブ"])
                                actuportpost = '000' + actuport
                        elif temp1actuname == 'ヒーター':
                                actuport = str(actudict["ヒーター"])
                                actuportpost = '000' + actuport
                        elif temp1actuname == '巻き上げ機':
                                actuport = str(actudict["巻き上げ機"])
                                actuportpost = '000' + actuport
			elif temp1actuname == '設定しない':
                                actuport = str(actudict["設定しない"]) 
                                actuportpost = '000' + actuport


			unit_id = unitlst.unit1_id
			
			con.row_factory = sqlite3.Row
			cur = con.cursor()
			str = "select  MAX(regdate),myid,s1,sense1,actuate1,interval1,mode1,s2,sense2,actuate2,interval2,mode2,s3,sense3,actuate3,interval3,mode3,s4,sense4,actuate4,interval4,mode4,s5,sense5,actuate5,interval5,mode5 from ctltbl where myid=" + "'"+ unit_id +"'"
			cur.execute(str)
			result = cur.fetchone()

			slide2 = form.getfirst('slide2','').encode('utf-8') 
			slide2pint = form.getfirst('slide2','')
			slide2int = int(slide2pint)
			if slide2int > 100 :
				slide2a = slide2
			elif slide2int < 10 :
				slide2a = '000' + slide2
				#slide2a = + slide2
			else:
				slide2a = '00' + slide2
				#slide2a = slide2

			myid = unitlst.unit1_id
			
			s1 =  result[2].encode('utf-8')
			sense1 =  result[3].encode('utf-8')
			actuate1 =  result[4].encode('utf-8')
			interval1 =  result[5].encode('utf-8')
			mode1 =  result[6].encode('utf-8')

			s2 = '7777'
			sense2 = '2222'
			actuate2 = actuportpost
			interval2 = slide2a
			mode2 = form.getfirst('temp1mode','').encode('utf-8')

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

			cur = con.cursor() 
			cur.execute("insert into ctltbl values(datetime('now','localtime'),?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(cgi.escape(myid),cgi.escape(s1), cgi.escape(sense1), cgi.escape(actuate1), cgi.escape(interval1),cgi.escape(mode1), cgi.escape(s2), cgi.escape(sense2), cgi.escape(actuate2), cgi.escape(interval2),cgi.escape(mode2), cgi.escape(s3), cgi.escape(sense3), cgi.escape(actuate3), cgi.escape(interval3),cgi.escape(mode3), cgi.escape(s4), cgi.escape(sense4), cgi.escape(actuate4), cgi.escape(interval4),cgi.escape(mode4), cgi.escape(s5), cgi.escape(sense5), cgi.escape(actuate5), cgi.escape(interval5),cgi.escape(mode5)))  
			con.commit()  


  		elif command == 'temp2' and temp2actuname != 'na':	

			if temp2actuname == '潅水チューブ':
                                actuport = str(actudict["潅水チューブ"])
                                actuportpost = '000' + actuport
                        elif temp2actuname == 'ヒーター':
                                actuport = str(actudict["ヒーター"])
                                actuportpost = '000' + actuport
                        elif temp2actuname == '巻き上げ機':
                                actuport = str(actudict["巻き上げ機"])
                                actuportpost = '000' + actuport
			elif temp2actuname == '設定しない':
                                actuport = str(actudict["設定しない"]) 
                                actuportpost = '000' + actuport

			unit_id = unitlst.unit1_id
			
			con.row_factory = sqlite3.Row
			cur = con.cursor()
			str = "select  MAX(regdate),myid,s1,sense1,actuate1,interval1,mode1,s2,sense2,actuate2,interval2,mode2,s3,sense3,actuate3,interval3,mode3,s4,sense4,actuate4,interval4,mode4,s5,sense5,actuate5,interval5,mode5 from ctltbl where myid=" + "'"+ unit_id +"'"
			cur.execute(str)
			result = cur.fetchone()

			slide3 = form.getfirst('slide3','').encode('utf-8') 
			slide3pint = form.getfirst('slide3','')
			slide3int = int(slide3pint)
			if slide3int >= 100 :
				slide3a = '0' + slide3
			elif slide3int < 10 :
				slide3a = '000' + slide3
			else:
				slide3a = '00' + slide3

			myid = unitlst.unit1_id
		
                        s1 =  result[2].encode('utf-8')
                        sense1 =  result[3].encode('utf-8')
                        actuate1 =  result[4].encode('utf-8')
                        interval1 =  result[5].encode('utf-8')
                        mode1 =  result[6].encode('utf-8')

                        s2 = result[7].encode('utf-8')
                        sense2 = result[8].encode('utf-8')
                        actuate2 = result[9].encode('utf-8')
                        interval2 = result[10].encode('utf-8')
                        mode2 = result[11].encode('utf-8')
                        
                        s3 = '7777'
                        sense3 = '3333'
                        actuate3 = actuportpost
                        interval3 = slide3a
                        mode3 = form.getfirst('temp2mode','').encode('utf-8')

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

			cur = con.cursor() 
			cur.execute("insert into ctltbl values(datetime('now','localtime'),?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(cgi.escape(myid),cgi.escape(s1), cgi.escape(sense1), cgi.escape(actuate1), cgi.escape(interval1),cgi.escape(mode1), cgi.escape(s2), cgi.escape(sense2), cgi.escape(actuate2), cgi.escape(interval2),cgi.escape(mode2), cgi.escape(s3), cgi.escape(sense3), cgi.escape(actuate3), cgi.escape(interval3),cgi.escape(mode3), cgi.escape(s4), cgi.escape(sense4), cgi.escape(actuate4), cgi.escape(interval4),cgi.escape(mode4), cgi.escape(s5), cgi.escape(sense5), cgi.escape(actuate5), cgi.escape(interval5),cgi.escape(mode5)))  
			con.commit()  


  		elif command == 'humed' and humedactuname != 'na':	

                        if humedactuname == '潅水チューブ':
                                actuport = str(actudict["潅水チューブ"])
                                actuportpost = '000' + actuport
                        elif humedactuname == 'ヒーター':
                                actuport = str(actudict["ヒーター"])
                                actuportpost = '000' + actuport
                        elif humedactuname == '巻き上げ機':
                                actuport = str(actudict["巻き上げ機"])
                                actuportpost = '000' + actuport
			elif humedactuname == '設定しない':
                                actuport = str(actudict["設定しない"]) 
                                actuportpost = '000' + actuport

			unit_id = unitlst.unit1_id
			con.row_factory = sqlite3.Row
			cur = con.cursor()
			str = "select  MAX(regdate),myid,s1,sense1,actuate1,interval1,mode1,s2,sense2,actuate2,interval2,mode2,s3,sense3,actuate3,interval3,mode3,s4,sense4,actuate4,interval4,mode4,s5,sense5,actuate5,interval5,mode5 from ctltbl where myid=" + "'"+ unit_id +"'"
			cur.execute(str)
			result = cur.fetchone()
			#print result

			slide4 = form.getfirst('slide4','').encode('utf-8') 
			slide4pint = form.getfirst('slide4','')
			slide4int = int(slide4pint)
			if slide4int >= 100 :
				slide4a = '0' + slide4
			elif slide4int < 10 :
				slide4a = '000' + slide4
			else:
				slide4a = '00' + slide4

			myid = unitlst.unit1_id

                        s1 =  result[2].encode('utf-8')
                        sense1 =  result[3].encode('utf-8')
                        actuate1 =  result[4].encode('utf-8')
                        interval1 =  result[5].encode('utf-8')
                        mode1 =  result[6].encode('utf-8')

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
                        
                        s4 = '7777'
                        sense4 = '4444'
                        actuate4 = actuportpost
                        interval4 = slide4a
                        mode4 = form.getfirst('humedmode','').encode('utf-8')

                        s5 = result[22].encode('utf-8')
                        sense5 = result[23].encode('utf-8')
                        actuate5 = result[24].encode('utf-8')
                        interval5 = result[25].encode('utf-8')
                        mode5 = result[26].encode('utf-8')

			cur = con.cursor() 
			cur.execute("insert into ctltbl values(datetime('now','localtime'),?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(cgi.escape(myid),cgi.escape(s1), cgi.escape(sense1), cgi.escape(actuate1), cgi.escape(interval1),cgi.escape(mode1), cgi.escape(s2), cgi.escape(sense2), cgi.escape(actuate2), cgi.escape(interval2),cgi.escape(mode2), cgi.escape(s3), cgi.escape(sense3), cgi.escape(actuate3), cgi.escape(interval3),cgi.escape(mode3), cgi.escape(s4), cgi.escape(sense4), cgi.escape(actuate4), cgi.escape(interval4),cgi.escape(mode4), cgi.escape(s5), cgi.escape(sense5), cgi.escape(actuate5), cgi.escape(interval5),cgi.escape(mode5)))  
			con.commit()  

  		elif command == 'light':	

                        if lightactuname == '潅水チューブ':
                                actuport = str(actudict["潅水チューブ"])
                                actuportpost = '000' + actuport
                        elif lightactuname == 'ヒーター':
                                actuport = str(actudict["ヒーター"])
                                actuportpost = '000' + actuport
                        elif lightactuname == '巻き上げ機':
                                actuport = str(actudict["巻き上げ機"])
                                actuportpost = '000' + actuport
			elif lightactuname == '設定しない':
                                actuport = str(actudict["設定しない"]) 
                                actuportpost = '000' + actuport

			unit_id = unitlst.unit1_id
			con.row_factory = sqlite3.Row
			cur = con.cursor()
			str = "select  MAX(regdate),myid,s1,sense1,actuate1,interval1,mode1,s2,sense2,actuate2,interval2,mode2,s3,sense3,actuate3,interval3,mode3,s4,sense4,actuate4,interval4,mode4,s5,sense5,actuate5,interval5,mode5 from ctltbl where myid=" + "'"+ unit_id +"'"
			cur.execute(str)
			result = cur.fetchone()

			slide5 = form.getfirst('slide5','').encode('utf-8') 
			slide5pint = form.getfirst('slide5','')
			slide5int = int(slide5pint)
			if slide5int >= 1000 :
				slide5a = slide5
			elif slide5int < 1000 and slide5int >= 100  :
				slide5a = '0' + slide5
			elif slide5int < 100 and slide5int >= 10 :
				slide5a = '00' + slide5
			else:
				slide5a = '000' + slide5

			myid = unitlst.unit1_id

 			s1 =  result[2].encode('utf-8')
                        sense1 =  result[3].encode('utf-8')
                        actuate1 =  result[4].encode('utf-8')
                        interval1 =  result[5].encode('utf-8')
                        mode1 =  result[6].encode('utf-8')

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

                        s5 = '7777'
                        sense5 = '5555'
                        actuate5 = actuportpost
                        interval5 = slide5a
                        mode5 = form.getfirst('lightdmode','').encode('utf-8')

			cur = con.cursor() 
			cur.execute("insert into ctltbl values(datetime('now','localtime'),?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(cgi.escape(myid),cgi.escape(s1), cgi.escape(sense1), cgi.escape(actuate1), cgi.escape(interval1),cgi.escape(mode1), cgi.escape(s2), cgi.escape(sense2), cgi.escape(actuate2), cgi.escape(interval2),cgi.escape(mode2), cgi.escape(s3), cgi.escape(sense3), cgi.escape(actuate3), cgi.escape(interval3),cgi.escape(mode3), cgi.escape(s4), cgi.escape(sense4), cgi.escape(actuate4), cgi.escape(interval4),cgi.escape(mode4), cgi.escape(s5), cgi.escape(sense5), cgi.escape(actuate5), cgi.escape(interval5),cgi.escape(mode5)))  
			con.commit()  


	else:
			unit_id = unitlst.unit1_id
			con.row_factory = sqlite3.Row
			cur = con.cursor()
			str = "select  MAX(regdate),myid,s1,sense1,actuate1,interval1,mode1,s2,sense2,actuate2,interval2,mode2,s3,sense3,actuate3,interval3,mode3,s4,sense4,actuate4,interval4,mode4,s5,sense5,actuate5,interval5,mode5 from ctltbl where myid=" + "'"+ unit_id +"'"
			cur.execute(str)
			result = cur.fetchone()

			myid = unitlst.unit1_id
		

                        s1 =  result[2].encode('utf-8')
                        sense1 =  result[3].encode('utf-8')
                        actuate1 =  result[4].encode('utf-8')
                        interval1 =  result[5].encode('utf-8')
                        mode1 =  result[6].encode('utf-8')

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
	
			cur = con.cursor() 
			cur.execute("insert into ctltbl values(datetime('now','localtime'),?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(cgi.escape(myid),cgi.escape(s1), cgi.escape(sense1), cgi.escape(actuate1), cgi.escape(interval1),cgi.escape(mode1), cgi.escape(s2), cgi.escape(sense2), cgi.escape(actuate2), cgi.escape(interval2),cgi.escape(mode2), cgi.escape(s3), cgi.escape(sense3), cgi.escape(actuate3), cgi.escape(interval3),cgi.escape(mode3), cgi.escape(s4), cgi.escape(sense4), cgi.escape(actuate4), cgi.escape(interval4),cgi.escape(mode4), cgi.escape(s5), cgi.escape(sense5), cgi.escape(actuate5), cgi.escape(interval5),cgi.escape(mode5)))  
			con.commit()  

		 	con.close()	
        		cur.close()




unit_id = unitlst.unit1_id
 
print "<h2>You are all set</h2>"

# put your controller's IP addr and path here
print myurl
print "</td></tr></table></center>" 
print "</body></html>"  

