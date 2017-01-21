#-*- coding:utf-8 -*-
import BaseHTTPServer
import urlparse
import os, sys,thread, time
import serial
import ptmsg
import urllib2
import json

class MyReceiver(ptmsg.PTReceiver):
	DATA = None
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
		if data.has_key('formaldehyde'):
			data['formaldehyde'] = '%.3f' % (data['formaldehyde'] / 100.0)
		if data.has_key('temperature'):
			data['temperature'] = '%.1f' % (data['temperature'] / 10.0)
		if data.has_key('humidity'):
			data['humidity'] = '%.1f%%' % (data['humidity'] / 10.0)
		if data.has_key('cnt_0p3'):
			data['cnt_0p3'] = format(data['cnt_0p3'], ',')
		if data.has_key('cnt_0p5'):
			data['cnt_0p5'] = format(data['cnt_0p5'], ',')
		if data.has_key('cnt_2p5'):
			data['cnt_2p5'] = format(data['cnt_2p5'], ',')
		if data.has_key('cnt_5p0'):
			data['cnt_5p0'] = format(data['cnt_5p0'], ',')
		if data.has_key('cnt_10p0'):
			data['cnt_10p0'] = format(data['cnt_10p0'], ',')
		data['time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
		MyReceiver.DATA = data

def ReadData():
	port = '/dev/ttyS0'
	ser = serial.Serial(port, 9600, timeout = 1)
	msg = ptmsg.PTMsg()
	msg.setReceiver(MyReceiver())
	while True:
		data = ser.read(40)
		msg.feed(data)
	ser.close()


STATICS = {
	'/' : ('text/html', 'static/index.html'),
	'/jquery.js' : ('application/x-javascript', 'static/jquery.js'),
	'/style.css' : ('text/css', 'static/style.css'),
}

ROOT = os.path.split(os.path.abspath(sys.argv[0]))[0] + '/'



class AirRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_GET(self):
		result = urlparse.urlparse(self.path)
		_GET = urlparse.parse_qs(result.query,True)
		if STATICS.has_key(result.path):
			info = STATICS[result.path]
			self.send_response(200)
			self.send_header('Content-Type', info[0])
			fp = open(ROOT + info[1], 'rb')
			data = fp.read()
			fp.close()
			self.send_header("Content-Length", str(len(data)))
			self.end_headers()
			self.wfile.write(data)
			return
	def do_POST(self):
		result = urlparse.urlparse(self.path)
		if result.path == '/refresh':
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			data = json.dumps(MyReceiver.DATA)
			self.send_header("Content-Length", str(len(data)))
			self.end_headers()
			self.wfile.write(data)
			return

#----------------------------------------------------------------------

if __name__ == '__main__':
	thread.start_new_thread(ReadData, ()) 
	server = BaseHTTPServer.HTTPServer(('', 80), AirRequestHandler)
	server.serve_forever()