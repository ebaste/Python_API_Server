#!/usr/bin/env python
# -*- coding: utf-8 -*-

from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn
import threading
import argparse
import re
import cgi

# To create the server you should use: python simplewebserver.py port ip
# for example: python simplewebserver.py 8080 127.0.0.1 

# With the POST intructions you store JSON data in the server.
# POST record example using curl:
# curl -X POST http://localhost:8080/api/v1/addrecord/1 -d '{"asif":"test1"}' -H 'Content-Type: application/json'
# curl -X POST http://localhost:8080/api/v1/addrecord/2 -d '{"asif":"test2"}' -H 'Content-Type: application/json'
# curl -X POST http://localhost:8080/api/v1/addrecord/3 -d '{"asif":"test3"}' -H 'Content-Type: application/json'

# You can recover the data with GET:

# GET record example using curl:
# curl -X GET http://localhost:8080/api/v1/getrecord/1 -H 'Content-Type: application/json'
# curl -X GET http://localhost:8080/api/v1/getrecord/2 -H 'Content-Type: application/json'
# curl -X GET http://localhost:8080/api/v1/getrecord/3 -H 'Content-Type: application/json'


# The object where you'll store the JSON objects 
class LocalData(object):
	records = {}
 
class HTTPRequestHandler(BaseHTTPRequestHandler):

# The POST part

 def do_POST(self):
# The URL info of the API
# http://localhost:8080/api/v1/addrecord/1
# The number '1' is the key of the object
 	if None != re.search('/api/v1/addrecord/*', self.path):
 		ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
 		if ctype == 'application/json':
# We need that the content type will be 'application/json'
			length = int(self.headers.getheader('content-length'))
 			data = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
 			recordID = self.path.split('/')[-1]
 			LocalData.records[recordID] = data
 			print "record %s is added successfully" % recordID
 		else:
# If the object type is differente from 'application/json' the server don`t store anything 
 			data = {}
 
 		self.send_response(200)
 		self.end_headers()
 	else:
# If the URL is not correct, the server returns a 403 Error.
 		self.send_response(403)
 		self.send_header('Content-Type', 'application/json')
 		self.end_headers()
 
 	return
 
# The GET part
 
 def do_GET(self):
# http://localhost:8080/api/v1/addrecord/1
# The number '1' is the key of the object we want to get
# Ther is some thing to fix, with /api/v1/getrecords also works
 	if None != re.search('/api/v1/getrecord/*', self.path):
 		recordID = self.path.split('/')[-1]
 		if LocalData.records.has_key(recordID):
# If there is a record with the key, it returns the value and a 200 code
 			self.send_response(200)
 			self.send_header('Content-Type', 'application/json')
 			self.end_headers()
 			self.wfile.write(LocalData.records[recordID])
 		else:
# If there isn't a record with the key, it returns a 400 error
 			self.send_response(400, 'Bad Request: record does not exist')
 			self.send_header('Content-Type', 'application/json')
 			self.end_headers()
 	else:
# If the URL is not valid, it returns a 403 error 		
 		self.send_response(403)
 		self.send_header('Content-Type', 'application/json')
 		self.end_headers()
 
	return
 
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	allow_reuse_address = True
 
 	def shutdown(self):
 		self.socket.close()
 		HTTPServer.shutdown(self)
 
class SimpleHttpServer():

	def __init__(self, ip, port):
 		self.server = ThreadedHTTPServer((ip,port), HTTPRequestHandler)
 
	def start(self):
 		self.server_thread = threading.Thread(target=self.server.serve_forever)
 		self.server_thread.daemon = True
 		self.server_thread.start()

 	def waitForThread(self):
 		self.server_thread.join()
 
	def addRecord(self, recordID, jsonEncodedRecord):
		LocalData.records[recordID] = jsonEncodedRecord
 
	def stop(self):
		self.server.shutdown()	
		self.waitForThread()
 
if __name__=='__main__':
	parser = argparse.ArgumentParser(description='HTTP Server')
	parser.add_argument('port', type=int, help='Listening port for HTTP Server')
	parser.add_argument('ip', help='HTTP Server IP')
	args = parser.parse_args()
 
	server = SimpleHttpServer(args.ip, args.port)
	print 'HTTP Server Running...........'
	server.start()
	server.waitForThread()
