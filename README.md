# rSense "Makashitakun"
Welcome! rSense "Makashitakun" is the automated vegetable cultivation system which is built up with Arduino and Raspberry Pi. Arduino is used for collecting sensors data and handling actuators. Raspberry Pi is used for controller which manage all Arduino units to work properly and hooked up to the internet in order to manage from anywhere in the world. Both units are connected via Xbee module. I have upped and been running "Makashitakun" for indoor vegetable farm to manage watering and temperature control. It runs great, I can check current status, change threshold value, start/stop actuator forcefully from home or even while traveling. You get the idea? Have fun!
<pre>
<h3>Content:</h3>
Arduino/
  rSense-diy_xxx.ino 
   This is for sensor unit which handle sensors and actuators.

Raspberry-Pi/
  cgi-bin/
    forcectl.cgi
     - To start/stop actuator forcefully.
    persist.cgi
     - To syncronize controller's threshold value to sensor unit.
    setvalues.cgi
     - To save controller's threshold value to data base.
    unitlst.py
     - Store Xbee information of target units.
     
  sbin/
    requestAndsavedata.py
     - Request to send current data and saving data in data base.
     
  www/
    rsensectl.psp
     - This is python script for web based control panel.

* Please make sure to install the following additions and set Xbee to API mode.
  <a href="https://code.google.com/p/xbee-arduino/" target=_blank>Xbee-Arduino</a>
  <a href="https://pypi.python.org/pypi/XBee" target=_blank>Python-xbee</a>
  
I have used DHT library for humidity and temperature, you might end up with using other stuff.

<a href="http://rsensesystems.com/rsensediy" target=_blank>http://rsensesystems.com/rsensediy</a>
</pre>

