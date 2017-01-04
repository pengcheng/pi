import serial
import ptmsg
import urllib2

class MyReceiver(ptmsg.PTReceiver):
  def onReceive(self, data, rawdata):
    if not data:
      print 'empty data'
      return
    if not data.has_key('check'):
      print 'missing check'
      return
    if not data.has_key('check_data'):
      print 'missing check in data'
      return
    if data['check'] != data['check_data']:
      print 'check not match'
      return
    try:
      urllib2.urlopen('http://w.cubexp.com/upload/' + rawdata).read()
    except: pass
    print 'PM2.5: %d\t%d\t%d' % (data['pm2.5'], data['pm2.5_air'], data['cnt_2.5'])

port = '/dev/ttyS0'
ser = serial.Serial(port, 9600, timeout = 1)
msg = ptmsg.PTMsg()
msg.setReceiver(MyReceiver())

while True:
  data = ser.read(40)
  msg.feed(data)
ser.close()
